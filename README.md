# 🚨 ResQHub: Disaster Relif Sysyem

> **Tagline:** A smart, crassh_proof emergency management system that works even withiut the internet.
> **Team Name:** LogicLoop

---

## 📌 Problem Statement

During disasterr like floods or earthquakes, communication system fail drastically:
* ✖️ **Network Blackout:** 3G/4G/5G mobile internet and cell towers get destroyed or shut down.
* ✖️ **Control Room Chaos:** Managing thousands of request makes it difficult to differntitate bte  high-risk critical victims and non-urgent request.
* ✖️ **Lack of donor Transparency:** Donors lack trust regarding whetherr their donated supplies or funds actually reach the victims in time.

---
## 💡 Our Solution (ResQHub)
ResQHub is a resilient, 3-layered disaster relief architecture designed to ensure zero faliure during emergency rescue operations:

* ⚡ **3-layered SOS Resilience:**
 1.  ** Layer 1 (Online Mode):** High -Speed fastApI endpoints when mobile network are active.
 2.   ** layer 2 (@G SMS Fallback):** Automatic background short 2G SMS triggering when internet connectivity drops.
 3.   ** layer 3 (Bluetooth Mesh Networking):** Peer-to-peer (Hop by-Hop) data transfer using Web Bluetooth when mobile towers completely collapse.
* 🏹 **Smart Priority Scoring Algorithm(1 to 10):** Automatically prioritizes critical cases (Medical & Trapped cases) to the top of the queue for the rescue control room.
* 🤝 **Donor Transparency Portal:** Real-time supply Tracking with Gps and photo proof-of-delievery for donors.

---
## ⚒️ Tech Stack
| Component | Technology Used |
| :--- | :--- |
| **Backend API** | Python (fastAPI + Pydantic) |
| **Frontend UI** | Html/CSS |
| **Database** | In-Memory Data Structure (Scalable to MySQL) |
| **offline Fallback** | 2G SMS Gateway Hook & web Bluetooth API |

---
