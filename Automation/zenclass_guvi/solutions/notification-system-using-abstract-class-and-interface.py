from abc import ABC, abstractmethod

class Notification(ABC):
    @abstractmethod
    def send(self, message):
        pass

class BaseNotification(Notification):
    def displayMessage(self, message):
        return message

class EmailNotification(BaseNotification):
    def send(self, message):
        return "Email: " + self.displayMessage(message)

class SMSNotification(BaseNotification):
    def send(self, message):
        return "SMS: " + self.displayMessage(message)

class PushNotification(BaseNotification):
    def send(self, message):
        return "Push: " + self.displayMessage(message)

if __name__ == "__main__":
    notification_type = input().strip()
    message = input().strip()
    
    if notification_type == "email":
        notification = EmailNotification()
    elif notification_type == "sms":
        notification = SMSNotification()
    elif notification_type == "push":
        notification = PushNotification()
    else:
        print(-1)
        exit()
    
    print(notification.send(message))
