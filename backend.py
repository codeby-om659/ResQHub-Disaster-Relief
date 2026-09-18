from fastapi import FastAPI,HTTPException,Form,Request
# Form ka use dat handle karne ke lye,jab ham html form se bheja gaya hua data recieve karna chate hai jaise ki userr name,password,age
#Request ka use  jab hame client dwara bheji gayi puri http request ki axis chayie
from fastapi.middleware.cors import CORSMiddleware
# corsmiddleware ka main kam alag alg domain  kr bbech mai security restriction ko manage karna hai
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional,List
from datetime import datetime

app=FastAPI(
    title="ResQHub - Disaster Relief Centeral Backend API",
    description="backend supporting 3- layer  SOS System(Internet,2G,BLE MEsh)",
    version="1.0"
)

#frontend connection allowed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
# DATABASE
sos_datbase=[]
donation_database=[
    {
        "id":1,
        "donor_name":"ratan tata foundation",
        "item":"1000 food Packets",
        "camp_location":"relief Camp delhi-sector 4 ",
        "status":"delivered",
        "gps_proof":"28.6139,77.2090(photo verfied)"
    }
]

#  pydanticdata models
class SOSRequestModel(BaseModel):
    name:str
    phone:str
    location_lat:float
    location_long:float
    emergency_type:str #"medical",'trpped','supplies'
    affected_count:int #kitne log phase hue hai

class MeshSOSModel(BaseModel):
    emergency_type:str
    affected_coumt:int
    lat:float
    long:float
    hop_count:int #bina internet wala msg kitne phono ke dwara aayya hai
    relay_device_id:str #ye us aakhri mobile ka unique id hoga jisne us msg ko recieve karke internet ke jariye backend par upload kiya hai

class DonatioModel(BaseModel):
    donor_name:str
    item:str
    camp_location:str

# scor dene wala function
def calculate_priority_score(emergency_type:str,affected_count:int) ->int:
    """
    priority scoring algorithms (Score : 1 to 10)
    Gives highest priority to trapped and medical emerrgencies.
    """
    score=1
    if emergency_type=="trapped":
        score+=5
    elif emergency_type=="medical":
        score+=4
    elif emergency_type=="food_water":
        score+=2
    else:
        score+=1

    # affected people multiplier
    if affected_count>10:
        score+=3
    elif affected_count>3:
        score+=2
    else:
        score+=1
    return min(score,10)

# 1.============USER interface Endpoints
@app.get("/")
def root():
    return {"system":"ResQHub Backend","status":"Active"}
#Layer 1: Online SOS Submition Api
@app.post("/api/user/sos")
def submit_online(data:SOSRequestModel):
    priority=calculate_priority_score(data.emergency_type,data.affected_count)

    sos_entry={
        "id":len(sos_datbase)+1,
        "name":data.name,
        "phone":data.phone,
        "lat":data.location_lat,
        "long":data.location_long,
        "type":data.emergency_type,
        "count":data.affected_count,
        "priority":priority,
        "status":"Pending",
        "timestamp":datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    sos_datbase.append(sos_entry)
    #sort automatically by priority(highest firrst)
    sos_datbase.sort(key=lambda x:x["priority"],reverse=True)

    return {
        "status":"succes",
        "message":"SOS recieve Succesfully",
        "assigned_priority": priority,
        "data":sos_entry
    }

#Layer 2: 2G SMS Receiver Webhook (for offline sms)
@app.post("/api/user/sms-webhook")
async def receive_2g_sms_sos(From:str=Form(...),Body:str=Form(...)):
    #jab koi task time leta hai to  tab program rokne ke bajaye doosre task ko execute karta hai
    """
    Receives incoming SMS from Twilio/gsm Gateway
    Expected Body Format :sostrapped 5 28.6139 77.2090
    """
    try:
        parts =Body.strip().split(" ")
        if parts[0].upper()=="SOS":
            emergency_type=parts[1].lower()
            affected_count=int(parts[2])
            lat=float(parts[3])
            long=float(parts[4])

            priority=calculate_priority_score(emergency_type,affected_count)

            sos_entry={
                "id":len(sos_datbase)+1,
                "name":f"user({From})",
                "phone":From,
                "lat":lat,
                "long":long,
                "type":emergency_type,
                "count":affected_count,
                "priority":priority,
                "mode":"2G_SMS",
                "status":"Pending",
                "timestamp":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            sos_datbase.append(sos_entry)
            sos_datbase.sort(key=lambda x:x["priority"],reverse=True)

            xml_response="<Response><Message>ResQhub:SOS Recieved via 2GSMS. Rescue Team alered.</Message></Response>"
            return Response(content=xml_response,media_type="application/xml")

    except Exception:
        xml_error="<Response><Message>ResQhub:Invalid SMS Format .</Message></Response>"
        return Response(content=xml_error,media_type="application/xml")

#layer 3: Bluetooth mesh Relay sync Enpoint
@app.post("/api/user/mesh-sync")
def sync_bluetooth_mesh_sos(data:MeshSOSModel):
    priority=calculate_priority_score(data.emergency_type,data.affected_coumt)

    mesh_entry={
        "id":len(sos_datbase)+1,
        "name":data.name,
        "phone":data.phone,
        "lat":data.location_lat,
        "long":data.location_long,
        "type":data.emergency_type,
        "count":data.affected_count,
        "priority":priority,
        "mode":f"BLE_MEsh (Hops:{data.hop_count})",
        "status":"Pending",
        "timestamp":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    sos_datbase.append(mesh_entry)
    sos_datbase.sort(key=lambda x:x["priority"],reverse=True)
    return {"status":"SUCCESS","message":"Bluetooth Mesh Data Synced!"}

#======================2. CONTROL ROOM INTER FACE ENDPOINT
#fetch all emergency alert sorted by priority
@app.get("/api/control-room/queue")
def get_control_room_priority_queue():
    return {
        "total_request":len(sos_datbase),
        "priority_sorted queue": sos_datbase
    }

#update SOS Status (Dispatch Rescue/Resolved)
@app.put("/api/control-room/update-status/{sos-id}")
def update_rescue_status(sos_id:int,status :str):
    for item in sos_datbase:
        if item["id"]== sos_id:
            item["status"]= status.upper()
            return {"status":"success","message":f"SOS #{sos_id}updated to {status.upper()}"}
    raise HTTPException(status_code=404,detail="SOS ID not found")

#===================3.DONOR PORTAL INTERFFACE ENDPOINT==================
@app.get("/api/donor/list")
def get_donation_list():
    return {"total_donations":len(donation_database),"donations":donation_database }

#Register new donation
@app.post("/api/donor/add")
def add_new_donation(data:DonatioModel):
    doantion_entry={
        "id":len(donation_database),
        "donor_name":data.donor_name,
        "item":data.item,
        "camp_location":data.camp_location,
        "status":"IN_TRANSIT",
        "gps_proof":"Dispatch pending"
    }
    donation_database.append(doantion_entry)
    return {"status":"SUCCESS","data":doantion_entry}
