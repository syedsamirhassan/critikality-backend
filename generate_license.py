#!/usr/bin/env python3
"""
Critikality License Generator
Run this on your development machine to create customer licenses
"""

import json
import argparse
from datetime import datetime, timedelta
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import base64

class LicenseGenerator:
    def __init__(self):
        self.private_key = None
        self.public_key = None
    
    def generate_keys(self):
        """Generate RSA key pair (run once, save keys securely)"""
        print("Generating RSA-2048 key pair...")
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
        
        # Save private key (KEEP SECRET!)
        with open('private_key.pem', 'wb') as f:
            f.write(self.private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        # Save public key (ship with software)
        with open('public_key.pem', 'wb') as f:
            f.write(self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))
        
        print("✅ Keys generated:")
        print("   - private_key.pem (KEEP SECRET - used to generate licenses)")
        print("   - public_key.pem (ship with software - used to validate)")
    
    def load_private_key(self):
        """Load existing private key"""
        with open('private_key.pem', 'rb') as f:
            self.private_key = serialization.load_pem_private_key(
                f.read(),
                password=None,
                backend=default_backend()
            )
    
    def create_license(self, customer, site_id, jetson_serial, duration_months, max_cameras, features):
        """Create a signed license file"""
        
        # Calculate dates
        issued = datetime.now()
        expiration = issued + timedelta(days=duration_months * 30)
        
        # License data
        license_data = {
            "customer": customer,
            "site_id": site_id,
            "jetson_serial": jetson_serial,
            "issued_date": issued.strftime("%Y-%m-%d"),
            "expiration_date": expiration.strftime("%Y-%m-%d"),
            "max_cameras": max_cameras,
            "features": features,
            "version": "1.0"
        }
        
        # Convert to JSON and sign
        license_json = json.dumps(license_data, sort_keys=True)
        signature = self.private_key.sign(
            license_json.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        # Create final license with signature
        final_license = {
            **license_data,
            "signature": base64.b64encode(signature).decode()
        }
        
        # Save to file
        filename = f"{site_id}.lic"
        with open(filename, 'w') as f:
            json.dump(final_license, f, indent=2)
        
        print(f"✅ License created: {filename}")
        print(f"   Customer: {customer}")
        print(f"   Site: {site_id}")
        print(f"   Jetson: {jetson_serial}")
        print(f"   Cameras: {max_cameras}")
        print(f"   Valid until: {expiration.strftime('%Y-%m-%d')}")
        
        return filename

def main():
    parser = argparse.ArgumentParser(description='Generate Critikality licenses')
    parser.add_argument('--generate-keys', action='store_true', help='Generate new RSA key pair')
    parser.add_argument('--customer', help='Customer name')
    parser.add_argument('--site-id', help='Site identifier (e.g., ARAMCO-RT-001)')
    parser.add_argument('--jetson-serial', help='Jetson serial number')
    parser.add_argument('--cameras', type=int, default=4, help='Max cameras allowed')
    parser.add_argument('--duration', type=int, default=12, help='License duration in months')
    parser.add_argument('--features', nargs='+', default=['face_recognition', 'liveness', 'reports'],
                       help='Enabled features')
    
    args = parser.parse_args()
    
    generator = LicenseGenerator()
    
    if args.generate_keys:
        generator.generate_keys()
        return
    
    if not all([args.customer, args.site_id, args.jetson_serial]):
        parser.error('--customer, --site-id, and --jetson-serial are required')
    
    # Load private key
    generator.load_private_key()
    
    # Create license
    generator.create_license(
        customer=args.customer,
        site_id=args.site_id,
        jetson_serial=args.jetson_serial,
        duration_months=args.duration,
        max_cameras=args.cameras,
        features=args.features
    )

if __name__ == '__main__':
    main()
