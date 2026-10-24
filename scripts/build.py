import json
import logging
import os
import plistlib
import sys
from pathlib import Path
from typing import Literal, Union
from pydantic import BaseModel
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.serialization import pkcs7


class GitHubFormatter(logging.Formatter):
    PREFIXES = {
        logging.DEBUG: "::debug::",
        logging.WARNING: "::warning::",
        logging.ERROR: "::error::",
        logging.CRITICAL: "::error::",
    }

    def format(self, record: logging.LogRecord):
        prefix = self.PREFIXES.get(record.levelno, "")
        return f"{prefix}{super().format(record)}"

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(GitHubFormatter("%(message)s"))

logging.basicConfig(level=logging.INFO, handlers=[handler])
logger = logging.getLogger(__name__)


class Config(BaseModel):
    id: str
    name: str
    description: str
    ips: list[str]
    https: str | None = None
    tls: str | None = None
    uuid1: str
    uuid2: str

class HTTPSDNSSettings(BaseModel):
    DNSProtocol: Literal["HTTPS"] = "HTTPS"
    ServerAddresses: list[str]
    ServerURL: str
    ServerName: None = None

class TLSDNSSettings(BaseModel):
    DNSProtocol: Literal["TLS"] = "TLS"
    ServerAddresses: list[str]
    ServerURL: None = None
    ServerName: str

DNSSettings = Union[HTTPSDNSSettings, TLSDNSSettings]

class PayloadContent(BaseModel):
    DNSSettings: DNSSettings
    PayloadIdentifier: str
    PayloadType: Literal["com.apple.dnsSettings.managed"] = "com.apple.dnsSettings.managed"
    PayloadUUID: str
    PayloadVersion: int = 1
    ProhibitDisablement: Literal[False] = False

class Profile(BaseModel):
    PayloadContent: list[PayloadContent]
    PayloadDescription: str
    PayloadDisplayName: str
    PayloadIdentifier: str
    PayloadRemovalDisallowed: Literal[False] = False
    PayloadScope: Literal["System"] = "System"
    PayloadType: Literal["Configuration"] = "Configuration"
    PayloadUUID: str
    PayloadVersion: int = 1

class DnsEndpoint(BaseModel):
    protocol: Literal["HTTPS", "TLS"]
    filename: str

class DnsProfile(BaseModel):
    id: str
    name: str
    endpoints: list[DnsEndpoint]


def _generate_config(profile: Profile) -> bytes:
    xml_bytes = plistlib.dumps(profile.model_dump(exclude_none=True), fmt=plistlib.FMT_XML)
    return xml_bytes

def _sign_config(xml_bytes: bytes, cert: x509.Certificate, key: serialization.PrivateFormat, chain: list[x509.Certificate]) -> bytes:
    builder = (
        pkcs7.PKCS7SignatureBuilder()
        .set_data(xml_bytes)
        .add_signer(cert, key, hashes.SHA256())
    )
    for ca in chain:
        builder = builder.add_certificate(ca)

    signed_der = builder.sign(
        serialization.Encoding.DER,
        [pkcs7.PKCS7Options.Binary, pkcs7.PKCS7Options.NoCapabilities],
    )
    return signed_der

def _save_signed_profile(signed_der: bytes, output_path: Path):
    output_path.write_bytes(signed_der)


output_dir = Path("out")


def main():
    output_dir.mkdir(exist_ok=True, parents=True)
    final_profiles: list[DnsProfile] = []
    final_profiles_file = output_dir / "providers.json"
    domain = os.getenv("DOMAIN")
    if not domain:
        raise ValueError("DOMAIN environment variable is not set")
    cert_base = Path("certbot/config/live") / domain


    cert = x509.load_pem_x509_certificate((cert_base / "cert.pem").read_bytes())
    key = serialization.load_pem_private_key((cert_base / "privkey.pem").read_bytes(), password=None)
    chain = x509.load_pem_x509_certificates((cert_base / "chain.pem").read_bytes())


    for x in Path("providers").rglob("*.json"):
        if not x.is_file():
            continue
        m = Config.model_validate_json(x.read_text())

        d: list[DNSSettings] = []
        if m.https:
            d.append(
                HTTPSDNSSettings(
                    ServerAddresses=m.ips,
                    ServerURL=m.https,
                ),
            )
        if m.tls:
            d.append(
                TLSDNSSettings(
                    ServerAddresses=m.ips,
                    ServerName=m.tls,
                ),
            )

        uploaded_files: list[DnsEndpoint] = []
        
        for sub in d:
            p = Profile(
                PayloadContent=[
                    PayloadContent(
                        DNSSettings=sub,
                        PayloadIdentifier=f"com.apple.dnsSettings.managed.{m.uuid2.lower()}.payload",
                        PayloadUUID=m.uuid2.upper(),
                    ),
                ],
                PayloadDescription=m.description,
                PayloadDisplayName=m.name,
                PayloadIdentifier=f"com.bunniesnu.apple-dns",
                PayloadUUID=m.uuid1.upper(),
            )

            xml_bytes = _generate_config(p)
            signed_der = _sign_config(xml_bytes, cert, key, chain)
            filename = f"{m.id}-{sub.DNSProtocol.lower()}.mobileconfig"
            _save_signed_profile(signed_der, output_dir / filename)
            uploaded_files.append(
                DnsEndpoint(
                    protocol=sub.DNSProtocol,
                    filename=filename,
                ),
            )
            logger.info(f"Generated signed profile for {m.id} ({sub.DNSProtocol})")

        final_profile = DnsProfile(
            id=m.id,
            name=m.name,
            endpoints=uploaded_files,
        )
        final_profiles.append(final_profile)

    final_profiles_file.write_text(json.dumps([p.model_dump(exclude_none=True) for p in final_profiles], indent=2))

if __name__ == "__main__":
    main()