import json

def event_create(zonaid) :
    return {
        "zona":zonaid,
        "dominio": "r53testdns.aws.com.",
        "dns": "test002",
        "action": "add",
        "ip": "10.0.1.10",
        "sharedserviceaccount":"123456789"
    }
    

def event_delete(zonaid) :
    return {
        "zona":zonaid,
        "dominio": "r53testdns.aws.com.",
        "dns": "test002",
        "action": "del",
        "ip": "10.0.1.10",
        "sharedserviceaccount":"123456789"
    }



