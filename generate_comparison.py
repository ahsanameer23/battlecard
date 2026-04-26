import csv

columns = [
    "Category",
    "Competitor Brand",
    "Competitor Model",
    "Equivalent TP-Link / Mercusys Model",
    "10/100 Mbps RJ45 Ports",
    "Gigabit RJ45 Ports",
    "Uplink / SFP Ports",
    "PoE Ports",
    "PoE Budget",
    "Casing",
    "Installation",
    "Switching Capacity",
    "MAC Address Table",
    "Jumbo Frame",
    "PoE Standard",
    "Extend Mode",
    "Priority Mode",
    "Isolation Mode",
    "Packet Forwarding Rate",
    "Fanless",
    "Management",
    "USPs for TP-Link/Mercusys"
]

data = [
    # Networking Channel Partners (Omada Easy Managed / TP-Link Business)
    ["Networking", "D-Link", "DGS-F1010P", "TL-SG1210P / TL-SG1210MP", "-", "9", "1 SFP", "8", "96W / 123W", "Metal", "Desktop / Wall-Mounting", "20 Gbps", "4K", "16 KB", "802.3af/at", "Yes", "Yes", "Yes", "14.88 Mpps", "Yes", "Easy Smart", "Higher PoE Budget, Omada integration options, Lifetime Warranty"],
    ["Networking", "D-Link", "DGS-F1016P", "TL-SG1218MPE", "-", "16", "2 SFP", "16", "150W", "Metal", "Rackmount", "36 Gbps", "8K", "10 KB", "802.3af/at", "Yes", "Yes", "Yes", "26.78 Mpps", "No", "Easy Smart", "Omada SDN integration, Intelligent Power Management"],
    ["Networking", "D-Link", "DGS-F1024P", "TL-SG1428PE", "-", "24", "2 SFP", "24", "250W", "Metal", "Rackmount", "56 Gbps", "8K", "9 KB", "802.3af/at", "Yes", "Yes", "Yes", "41.66 Mpps", "No", "Easy Smart / Smart", "More advanced management via Omada SDN, better switching capacity"],
    ["Networking", "D-Link", "DGS-F1026P", "TL-SG1428PE", "-", "24", "2 SFP", "24", "250W", "Metal", "Rackmount", "56 Gbps", "8K", "9 KB", "802.3af/at", "Yes", "Yes", "Yes", "41.66 Mpps", "No", "Easy Smart", "Robust Omada SDN features, Auto Recovery PoE"],
    ["Networking", "D-Link", "DGS-F1210-26PS-E", "TL-SG2428P", "-", "24", "4 SFP", "24", "250W", "Metal", "Rackmount", "56 Gbps", "8K", "9 KB", "802.3af/at", "Yes", "Yes", "Yes", "41.7 Mpps", "No", "Smart", "Omada SDN Cloud Access, Zero-Touch Provisioning, L2+ Features"],
    ["Networking", "D-Link", "DGS-1210-52MP", "TL-SG2452P", "-", "48", "4 SFP", "48", "370W", "Metal", "Rackmount", "104 Gbps", "16K", "9 KB", "802.3af/at", "No Info", "Yes", "Yes", "77.4 Mpps", "No", "Smart", "Omada Centralized Management, Strong IPv6 support"],
    ["Networking", "Ruijie", "RG-ES228GSP", "TL-SG2428P", "-", "24", "4 SFP", "24", "370W", "Metal", "Rackmount", "56 Gbps", "8K", "9 KB", "802.3af/at", "Yes", "Yes", "Yes", "41.66 Mpps", "No", "Smart", "Omada SDN Controller vs Ruijie Cloud, Local management options"],
    ["Networking", "Ruijie", "RG-ES228GSLP", "TL-SG2028P", "-", "24", "4 SFP", "24", "250W", "Metal", "Rackmount", "56 Gbps", "8K", "9 KB", "802.3af/at", "Yes", "Yes", "Yes", "41.66 Mpps", "No", "Smart", "Cost-effective Omada SDN alternative with comprehensive L2+"],
    ["Networking", "Ruijie", "RG-ES220GSP", "TL-SG2218P", "-", "16", "2 SFP", "16", "150W", "Metal", "Rackmount", "36 Gbps", "8K", "9 KB", "802.3af/at", "Yes", "Yes", "Yes", "26.7 Mpps", "No", "Smart", "Omada SDN, IP-MAC-Port Binding"],
    ["Networking", "Ruijie", "RG-ES220GSLP", "TL-SG2016P", "-", "16", "2 SFP", "16", "120W", "Metal", "Rackmount", "36 Gbps", "8K", "9 KB", "802.3af/at", "Yes", "Yes", "Yes", "26.7 Mpps", "No", "Smart", "Better local UI alongside SDN, robust security features"],

    # CCTV Market Models (Hikvision vs Mercusys / TP-Link Business LS series)
    ["CCTV", "Hikvision", "DS-3E1552P-SI", "TL-SG3452P", "-", "48", "4 SFP", "48", "380W", "Metal", "Rackmount", "104 Gbps", "16K", "9 KB", "802.3af/at", "Yes", "No Info", "Yes", "77.3 Mpps", "No", "Smart", "Omada App integration, 802.1x Authentication"],
    ["CCTV", "Hikvision", "DS-3E1526P-SI", "TL-SG1428PE", "-", "24", "2 SFP", "24", "225W", "Metal", "Rackmount", "52 Gbps", "8K", "9 KB", "802.3af/at", "Yes", "No Info", "Yes", "38.6 Mpps", "No", "Smart", "Higher PoE Auto Recovery, Ease of Use"],
    ["CCTV", "Hikvision", "DS-3E1528HP-SI-24P2T2F", "TL-SG2428P", "-", "24", "4 SFP/Combo", "24", "370W", "Metal", "Rackmount", "56 Gbps", "8K", "9 KB", "802.3af/at/bt", "Yes", "No Info", "Yes", "41.6 Mpps", "No", "Smart", "Rich VLAN features, Omada management"],
    ["CCTV", "Hikvision", "DS-3E1528P-SI-24P4F", "TL-SG2428P", "-", "24", "4 SFP", "24", "370W", "Metal", "Rackmount", "56 Gbps", "8K", "9 KB", "802.3af/at", "Yes", "No Info", "Yes", "41.6 Mpps", "No", "Smart", "Centralized Cloud Control"],
    ["CCTV", "Hikvision", "DS-3E1526P-SI-24P2F", "TL-SG1428PE", "-", "24", "2 SFP", "24", "225W", "Metal", "Rackmount", "52 Gbps", "8K", "9 KB", "802.3af/at", "Yes", "No Info", "Yes", "38.6 Mpps", "No", "Smart", "Reliable TP-Link warranty and local support"],
    ["CCTV", "Hikvision", "DS-3E1526P-EI", "LS1026G-PoE (Mercusys)", "-", "24", "2 SFP", "24", "250W", "Metal", "Rackmount", "52 Gbps", "8K", "9 KB", "802.3af/at", "Yes", "Yes", "Yes", "38.6 Mpps", "No", "Unmanaged", "Extremely competitive pricing via Mercusys, Plug and Play"],
    ["CCTV", "Hikvision", "DS-3E1326P-EI/M", "LS1026G-PoE (Mercusys)", "24", "2 (Combo)", "2 Combo", "24", "230W", "Metal", "Rackmount", "8.8 Gbps", "8K", "No Info", "802.3af/at", "Yes", "Yes", "Yes", "6.5 Mpps", "No", "Unmanaged", "Better reliability and availability, Extend mode up to 250m"],
    ["CCTV", "Hikvision", "DS-3E1326P-EI (B)", "LS1026G-PoE (Mercusys)", "24", "2 (Combo)", "2 Combo", "24", "230W", "Metal", "Rackmount", "8.8 Gbps", "8K", "No Info", "802.3af/at", "Yes", "Yes", "Yes", "6.5 Mpps", "No", "Unmanaged", "Better availability and robust power supply"],

    ["CCTV", "Hikvision", "DS-3E1518P-SI", "TL-SG1218MPE", "-", "16", "2 SFP", "16", "250W", "Metal", "Rackmount", "36 Gbps", "8K", "9 KB", "802.3af/at", "Yes", "No Info", "Yes", "26.7 Mpps", "No", "Smart", "Intelligent Power Management, Easy Smart Configuration UI"],
    ["CCTV", "Hikvision", "DS-3E1520HP-SI-16P2T2F", "TL-SG2218P", "-", "16", "2 SFP", "16", "150W", "Metal", "Rackmount", "36 Gbps", "8K", "9 KB", "802.3af/at/bt", "Yes", "No Info", "Yes", "26.7 Mpps", "No", "Smart", "Omada SDN Integration"],
    ["CCTV", "Hikvision", "DS-3E1518P-EI", "LS1018G-PoE (Mercusys)", "-", "16", "2 SFP", "16", "150W", "Metal", "Rackmount", "36 Gbps", "8K", "9 KB", "802.3af/at", "Yes", "Yes", "Yes", "26.7 Mpps", "No", "Unmanaged", "Plug & Play, Isolation Mode, Auto-Recovery"],
    ["CCTV", "Hikvision", "DS-3E1518P-SI-16P2F", "TL-SG1218MPE", "-", "16", "2 SFP", "16", "250W", "Metal", "Rackmount", "36 Gbps", "8K", "9 KB", "802.3af/at", "Yes", "No Info", "Yes", "26.7 Mpps", "No", "Smart", "TP-Link Easy Smart, QoS"],

    ["CCTV", "Hikvision", "DS-3E1318P-EI (B)", "LS1018G-PoE (Mercusys)", "16", "2 (Combo)", "2 Combo", "16", "230W", "Metal", "Rackmount", "7.2 Gbps", "8K", "No Info", "802.3af/at", "Yes", "Yes", "Yes", "5.3 Mpps", "No", "Unmanaged", "Full gigabit uplink on Mercusys vs Fast Ethernet on Hikvision"],
    ["CCTV", "Hikvision", "DS-3E1318P-EI/M", "LS1018G-PoE (Mercusys)", "16", "2 (Combo)", "2 Combo", "16", "130W", "Metal", "Rackmount", "7.2 Gbps", "8K", "No Info", "802.3af/at", "Yes", "Yes", "Yes", "5.3 Mpps", "No", "Unmanaged", "Better PoE Budget on Mercusys equivalent"],

    ["CCTV", "Hikvision", "DS-3E1510P-SI", "TL-SG1210MP", "-", "8", "2 SFP", "8", "123W", "Metal", "Desktop", "20 Gbps", "4K", "16 KB", "802.3af/at", "Yes", "No Info", "Yes", "14.8 Mpps", "Yes", "Smart", "Quiet Fanless design on smaller models, robust UI"],
    ["CCTV", "Hikvision", "DS-3E1512HP-SI-8P2T2F", "TL-SG2210MP", "-", "8", "2 SFP", "8", "150W", "Metal", "Desktop / Rack", "20 Gbps", "8K", "9 KB", "802.3af/at/bt", "Yes", "No Info", "Yes", "14.8 Mpps", "Yes", "Smart", "Omada App Control, Higher Security features"],
    ["CCTV", "Hikvision", "DS-3E1510P-EI", "LS109G-PoE / MS110P", "-", "8", "1 SFP / 1 RJ45", "8", "110W", "Metal", "Desktop", "20 Gbps", "4K", "16 KB", "802.3af/at", "Yes", "Yes", "Yes", "14.8 Mpps", "Yes", "Unmanaged", "Cost-effective unmanaged solution"],
    ["CCTV", "Hikvision", "DS-3E1510P-EI/M", "LS109G-PoE / MS110P", "-", "8", "1 SFP / 1 RJ45", "8", "60W", "Metal", "Desktop", "20 Gbps", "4K", "16 KB", "802.3af/at", "Yes", "Yes", "Yes", "14.8 Mpps", "Yes", "Unmanaged", "High value for money, 250m extend mode"],
    ["CCTV", "Hikvision", "DS-3E1510P-SI-8P2F", "TL-SG1210MP", "-", "8", "2 SFP", "8", "123W", "Metal", "Desktop", "20 Gbps", "4K", "16 KB", "802.3af/at", "Yes", "No Info", "Yes", "14.8 Mpps", "Yes", "Smart", "Centralized Management"],

    ["CCTV", "Hikvision", "DS-3E1309P-EI (B)", "LS109G-PoE (Mercusys)", "8", "1", "-", "8", "110W", "Metal", "Desktop", "1.8 Gbps", "4K", "No Info", "802.3af/at", "Yes", "Yes", "Yes", "1.3 Mpps", "Yes", "Unmanaged", "Gigabit model (LS109G) vs Fast Ethernet Hikvision at similar price point"],
    ["CCTV", "Hikvision", "DS-3E1310P-EI (B)", "LS109G-PoE (Mercusys)", "8", "2", "-", "8", "110W", "Metal", "Desktop", "5.6 Gbps", "4K", "No Info", "802.3af/at", "Yes", "Yes", "Yes", "4.1 Mpps", "Yes", "Unmanaged", "Gigabit model offers better bandwidth"],

    ["CCTV", "Hikvision", "DS-3E1505P-EI", "MS105GP (Mercusys)", "-", "5", "-", "4", "60W", "Metal", "Desktop", "10 Gbps", "2K", "9 KB", "802.3af/at", "Yes", "Yes", "Yes", "7.4 Mpps", "Yes", "Unmanaged", "More aggressive pricing, 65W PoE Budget on Mercusys"],
    ["CCTV", "Hikvision", "DS-3E1506P-EI", "MS108GP (Mercusys)", "-", "6", "-", "4", "60W", "Metal", "Desktop", "12 Gbps", "2K", "9 KB", "802.3af/at", "Yes", "Yes", "Yes", "8.9 Mpps", "Yes", "Unmanaged", "8 ports Gigabit on Mercusys for similar price"],
    ["CCTV", "Hikvision", "DS-3E1505P-EI/M", "MS105GP (Mercusys)", "-", "5", "-", "4", "45W", "Metal", "Desktop", "10 Gbps", "2K", "9 KB", "802.3af/at", "Yes", "Yes", "Yes", "7.4 Mpps", "Yes", "Unmanaged", "Higher PoE Budget (65W) on MS105GP vs 45W"],
    ["CCTV", "Hikvision", "DS-3E1506P-EI/M", "MS108GP (Mercusys)", "-", "6", "-", "4", "45W", "Metal", "Desktop", "12 Gbps", "2K", "9 KB", "802.3af/at", "Yes", "Yes", "Yes", "8.9 Mpps", "Yes", "Unmanaged", "Higher PoE Budget on Mercusys"],

    ["CCTV", "Hikvision", "DS-3E1105P-EI V2", "MS105GP (Mercusys)", "5", "-", "-", "4", "60W", "Metal", "Desktop", "1 Gbps", "2K", "No Info", "802.3af/at", "Yes", "Yes", "Yes", "0.7 Mpps", "Yes", "Unmanaged", "MS105GP offers Gigabit ports over Fast Ethernet Hikvision"],
    ["CCTV", "Hikvision", "DS-3E1106HP-EI", "MS108GP (Mercusys)", "6", "-", "-", "4", "60W", "Metal", "Desktop", "1.2 Gbps", "2K", "No Info", "802.3af/at/bt", "Yes", "Yes", "Yes", "0.8 Mpps", "Yes", "Unmanaged", "Gigabit ports vs Fast Ethernet"],
    ["CCTV", "Hikvision", "DS-3E1106P-EI", "MS108GP (Mercusys)", "6", "-", "-", "4", "60W", "Metal", "Desktop", "1.2 Gbps", "2K", "No Info", "802.3af/at", "Yes", "Yes", "Yes", "0.8 Mpps", "Yes", "Unmanaged", "Gigabit over Fast Ethernet"],
    ["CCTV", "Hikvision", "DS-3E1105P-EI/M V2", "MS105GP (Mercusys)", "5", "-", "-", "4", "45W", "Metal", "Desktop", "1 Gbps", "2K", "No Info", "802.3af/at", "Yes", "Yes", "Yes", "0.7 Mpps", "Yes", "Unmanaged", "65W PoE Budget + Gigabit on Mercusys MS105GP vs 45W Fast Ethernet"],
    ["CCTV", "Hikvision", "DS-3E1106P-EI/M", "MS108GP (Mercusys)", "6", "-", "-", "4", "45W", "Metal", "Desktop", "1.2 Gbps", "2K", "No Info", "802.3af/at", "Yes", "Yes", "Yes", "0.8 Mpps", "Yes", "Unmanaged", "65W PoE Budget + Gigabit on Mercusys vs Fast Ethernet"]
]

with open('comparison.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(columns)
    writer.writerows(data)

print("comparison.csv generated successfully.")
