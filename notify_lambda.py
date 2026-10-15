import json

def lambda_handler(event, context):
    # This function simulates an automated trigger when a new appointment is added to the database
    print("New Appointment Event Received: " + json.dumps(event))
    
    patient_name = event.get('patient_name', 'Unknown Patient')
    doctor_name = event.get('doctor_name', 'Unassigned Doctor')
    
    notification_message = f"Hello {patient_name}, your appointment with {doctor_name} is confirmed."
    print("Sending SMS/Email: ", notification_message)
    
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Notification sent successfully', 'details': notification_message})
    }