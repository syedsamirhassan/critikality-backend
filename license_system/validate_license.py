#!/usr/bin/env python3
"""
Critikality License Validator
Runs on Jetson to validate license files
"""

import json
import base64
from datetime import datetime, timedelta
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from pathlib import Path

class LicenseValidator:
    def __init__(self, public_key_path='public_key.pem'):
        with open(public_key_path, 'rb') as f:
            self.public_key = serialization.load_pem_public_key(
                f.read(),
                backend=default_backend()
            )
    
    def get_hardware_id(self):
        """Get Jetson serial number (hardware fingerprint)"""
        try:
            # Try Jetson-specific serial
            with open('/proc/device-tree/serial-number', 'r') as f:
                return f.read().strip()
        except:
            # Fallback to system serial
            try:
                import subprocess
                result = subprocess.run(['cat', '/sys/class/dmi/id/product_serial'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    return result.stdout.strip()
            except:
                pass
        
        # Last resort: MAC address
        try:
            import uuid
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) 
                           for i in range(0,8*6,8)][::-1])
            return f"MAC-{mac}"
        except:
            return "UNKNOWN"
    
    def validate_signature(self, license_data, signature):
        """Verify RSA signature"""
        try:
            license_json = json.dumps(license_data, sort_keys=True)
            signature_bytes = base64.b64decode(signature)
            
            self.public_key.verify(
                signature_bytes,
                license_json.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception as e:
            print(f"❌ Signature validation failed: {e}")
            return False
    
    def validate_license(self, license_path, grace_days=7):
        """
        Validate license file
        Returns: (valid, status_message, license_data)
        """
        
        # Load license file
        try:
            with open(license_path, 'r') as f:
                license_full = json.load(f)
        except Exception as e:
            return False, f"Cannot read license file: {e}", None
        
        # Extract signature
        signature = license_full.pop('signature', None)
        if not signature:
            return False, "License file is missing signature", None
        
        # Verify signature
        if not self.validate_signature(license_full, signature):
            return False, "License signature is invalid (tampered or corrupted)", None
        
        # Check hardware ID
        current_hw_id = self.get_hardware_id()
        licensed_hw_id = license_full.get('jetson_serial', '')
        
        if current_hw_id != licensed_hw_id and licensed_hw_id != "DEMO":
            return False, f"License is for different hardware (expected {licensed_hw_id}, got {current_hw_id})", license_full
        
        # Check expiration
        expiration_str = license_full.get('expiration_date')
        expiration = datetime.strptime(expiration_str, "%Y-%m-%d")
        now = datetime.now()
        days_remaining = (expiration - now).days
        
        if days_remaining < 0:
            # Expired - check grace period
            days_expired = abs(days_remaining)
            if days_expired <= grace_days:
                return True, f"⚠️  LICENSE EXPIRED {days_expired} days ago (grace period active)", license_full
            else:
                return False, f"License expired {days_expired} days ago (grace period ended)", license_full
        
        # Valid license
        if days_remaining <= 30:
            return True, f"✅ License valid ({days_remaining} days remaining - renewal recommended)", license_full
        else:
            return True, f"✅ License valid (expires {expiration_str})", license_full
    
    def get_license_info(self, license_path):
        """Get license information for display"""
        valid, message, data = self.validate_license(license_path)
        
        if not data:
            return {
                "valid": False,
                "message": message,
                "customer": "Unknown",
                "expiration": "Unknown"
            }
        
        return {
            "valid": valid,
            "message": message,
            "customer": data.get('customer', 'Unknown'),
            "site_id": data.get('site_id', 'Unknown'),
            "issued_date": data.get('issued_date', 'Unknown'),
            "expiration_date": data.get('expiration_date', 'Unknown'),
            "max_cameras": data.get('max_cameras', 0),
            "features": data.get('features', []),
            "hardware_id": data.get('jetson_serial', 'Unknown')
        }

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate Critikality license')
    parser.add_argument('license_file', help='Path to license file (.lic)')
    parser.add_argument('--public-key', default='public_key.pem', help='Path to public key')
    parser.add_argument('--show-hw-id', action='store_true', help='Show current hardware ID')
    
    args = parser.parse_args()
    
    validator = LicenseValidator(args.public_key)
    
    if args.show_hw_id:
        hw_id = validator.get_hardware_id()
        print(f"Current Hardware ID: {hw_id}")
        print(f"(Use this when generating license with --jetson-serial)")
        return
    
    # Validate license
    valid, message, data = validator.validate_license(args.license_file)
    
    print("=" * 60)
    print("CRITIKALITY LICENSE VALIDATION")
    print("=" * 60)
    print(f"Status: {message}")
    
    if data:
        print(f"\nCustomer: {data.get('customer')}")
        print(f"Site ID: {data.get('site_id')}")
        print(f"Issued: {data.get('issued_date')}")
        print(f"Expires: {data.get('expiration_date')}")
        print(f"Max Cameras: {data.get('max_cameras')}")
        print(f"Features: {', '.join(data.get('features', []))}")
        print(f"Hardware ID: {data.get('jetson_serial')}")
    
    print("=" * 60)
    
    return 0 if valid else 1

if __name__ == '__main__':
    exit(main())
