from interfaces.members.services.zk.zk import ZK
DEVICE_IP = '192.168.1.102'  
DEVICE_PORT = 4370 

def register_member_on_biometric(member):
    zk = ZK(DEVICE_IP, port=DEVICE_PORT, timeout=10)  # Increased timeout to 10 sec for safety
    conn = None

    try:
        print("Connecting to Biometric Device...")
        conn = zk.connect()
        conn.disable_device()

        # Fetch existing users to calculate next available ID
        users = conn.get_users()
        if users:
            # Safely parse integer user IDs (if device returns strings)
            user_ids = [int(user.user_id) for user in users if str(user.user_id).isdigit()]
            new_user_id = max(user_ids) + 1 if user_ids else 1
        else:
            new_user_id = 1  # If device is empty

        # Create user on the device
        full_name = f"{member.first_name} {member.last_name}".strip()
        conn.set_user(uid=new_user_id, name=full_name)

        print(f"User created on device with ID: {new_user_id}")

        conn.enable_device()
        conn.disconnect()

        return new_user_id

    except Exception as e:
        print(f"Biometric device error: {str(e)}")
        if conn:
            conn.disconnect()
        return None