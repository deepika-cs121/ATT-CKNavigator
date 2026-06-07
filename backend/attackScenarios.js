// NOTE: This is a .js file, not .ts
// All TypeScript interfaces and imports have been removed.

// --- SCENARIO DATABASE ---
export const scenarios = {
  // --- 1. RECONNAISSANCE (T1595) ---
  'Reconnaissance': {
    techniqueId: 'T1595',
    techniqueName: 'Active Scanning',
    nodes: [
      { id: 'attacker', name: 'Attacker', type: 'red' },
      { id: 'firewall', name: 'Firewall', type: 'neutral' },
      { id: 'webserver', name: 'Web Server', type: 'blue' },
      { id: 'unused_port', name: 'Port 8080', type: 'blue' },
    ],
    steps: [
      {
        step: 1,
        visual: { from: 'attacker', to: 'firewall', action: 'Nmap Scan (Top 100)' },
        redLog: { message: 'T1595: Initiating Nmap scan on target IP range.', severity: 'Low' },
        blueLog: { message: 'NIDS: Detected high volume of connection attempts from [Attacker IP]. Flagged as port scanning.', severity: 'Medium' },
      },
      {
        step: 2,
        visual: { from: 'attacker', to: 'webserver', action: 'Port 443 (HTTPS) Open' },
        redLog: { message: 'Scan results: Port 443 (HTTPS) is open.', severity: 'Low' },
        blueLog: null,
      },
      {
        step: 3,
        visual: { from: 'attacker', to: 'unused_port', action: 'Port 8080 (Jenkins) Open' },
        redLog: { message: 'Scan results: Port 8080 (Jenkins) is open and exposed.', severity: 'Medium' },
        blueLog: { message: 'SIEM: Alert! Non-standard port [8080] responded to external scan. Triage required.', severity: 'High' },
      },
    ],
  },

  // --- 2. RESOURCE DEVELOPMENT (T1583) ---
  'Resource Development': {
    techniqueId: 'T1583',
    techniqueName: 'Acquire Infrastructure',
    nodes: [
      { id: 'attacker', name: 'Attacker', type: 'red' },
      { id: 'registrar', name: 'Domain Registrar', type: 'neutral' },
      { id: 'c2', name: 'C2 Server (VPS)', type: 'red' },
    ],
    steps: [
      {
        step: 1,
        visual: { from: 'attacker', to: 'registrar', action: 'Register Typosquat Domain' },
        redLog: { message: 'T1583: Registered domain [micros0ft-login.com] for phishing campaign.', severity: 'Low' },
        blueLog: { message: 'Threat Intel: New domain [micros0ft-login.com] registered. Monitoring for suspicious activity.', severity: 'Low' },
      },
      {
        step: 2,
        visual: { from: 'attacker', to: 'c2', action: 'Setup C2 Server' },
        redLog: { message: 'T1583: Deployed C2 infrastructure on [VPS IP]. Ready for operations.', severity: 'Low' },
        blueLog: null,
      },
    ],
  },
  
  // --- 3. INITIAL ACCESS (T1566) ---
  'Initial Access': {
    techniqueId: 'T1566',
    techniqueName: 'Phishing',
    nodes: [
      { id: 'attacker', name: 'Attacker', type: 'red' },
      { id: 'gateway', name: 'Email Gateway', type: 'neutral' },
      { id: 'workstation', name: 'Workstation', type: 'blue' },
      { id: 'c2', name: 'C2 Server', type: 'red' },
    ],
    steps: [
      {
        step: 1,
        visual: { from: 'attacker', to: 'gateway', action: 'Send Phishing Email' },
        redLog: { message: 'T1566: Spearphishing email sent to [j.doe@corp.com].', severity: 'Low' },
        blueLog: { message: 'Email Gateway: Scanned 1 attachment from [micros0ft-login.com]. No malware found.', severity: 'Low' },
      },
      {
        step: 2,
        visual: { from: 'gateway', to: 'workstation', action: 'Email Delivered' },
        redLog: { message: 'Email delivered to user inbox.', severity: 'Low' },
        blueLog: { message: 'User [j.doe] opened email.', severity: 'Medium' },
      },
      {
        step: 3,
        visual: { from: 'workstation', to: 'c2', action: 'Malicious Beacon (SUCCESS)' },
        redLog: { message: 'T1204: User execution successful. Beacon established.', severity: 'High' },
        blueLog: { message: '**CRITICAL**: EDR: Suspicious outbound C2 traffic (T1071) detected from [WS-01] to [C2 IP].', severity: 'Critical' },
      },
    ],
  },
  
  // --- 4. EXECUTION (T1059) ---
  'Execution': {
    techniqueId: 'T1059',
    techniqueName: 'Command and Scripting',
    nodes: [
      { id: 'c2', name: 'Attacker (C2)', type: 'red' },
      { id: 'workstation', name: 'Workstation (Agent)', type: 'blue' },
      { id: 'powershell', name: 'PowerShell.exe', type: 'neutral' },
    ],
    steps: [
      {
        step: 1,
        visual: { from: 'c2', to: 'workstation', action: 'Send C2 Task' },
        redLog: { message: 'Tasking beacon on [WS-01] to execute PowerShell command.', severity: 'Low' },
        blueLog: { message: 'NIDS: Encrypted C2 heartbeat detected from [WS-01].', severity: 'Medium' },
      },
      {
        step: 2,
        visual: { from: 'workstation', to: 'powershell', action: 'Spawn PowerShell' },
        redLog: { message: 'T1059: Executing obfuscated PowerShell command to download script.', severity: 'Medium' },
        blueLog: { message: '**HIGH**: EDR: [Beacon.exe] spawned [powershell.exe] with obfuscated command line arguments.', severity: 'High' },
      },
    ],
  },

  // --- 5. PERSISTENCE (T1053) ---
  'Persistence': {
    techniqueId: 'T1053',
    techniqueName: 'Scheduled Task/Job',
    nodes: [
      { id: 'shell', name: 'Attacker (Shell)', type: 'red' },
      { id: 'workstation', name: 'Workstation', type: 'blue' },
      { id: 'scheduler', name: 'Task Scheduler', type: 'neutral' },
    ],
    steps: [
      {
        step: 1,
        visual: { from: 'shell', to: 'scheduler', action: 'Create Scheduled Task' },
        redLog: { message: 'T1053: Creating scheduled task "OneDriveUpdater" to run beacon on logon.', severity: 'Medium' },
        blueLog: { message: 'SIEM: New Scheduled Task "OneDriveUpdater" created on [WS-01] by [j.doe].', severity: 'Medium' },
      },
      {
        step: 2,
        visual: { from: 'scheduler', to: 'shell', action: 'Task Executed (SUCCESS)' },
        redLog: { message: 'Persistence successful. Task triggered after user logon.', severity: 'High' },
        blueLog: { message: '**HIGH**: EDR: Task "OneDriveUpdater" executed an unsigned binary from [C:\\Users\\j.doe\\AppData].', severity: 'High' },
      },
    ],
  },
  
  // --- 6. PRIVILEGE ESCALATION (T1068) ---
  'Privilege Escalation': {
    techniqueId: 'T1068',
    techniqueName: 'Exploitation for PrivEsc',
    nodes: [
      { id: 'shell', name: 'Attacker (User)', type: 'red' },
      { id: 'kernel', name: 'Windows Kernel', type: 'neutral' },
      { id: 'system_shell', name: 'Attacker (SYSTEM)', type: 'red' },
    ],
    steps: [
      {
        step: 1,
        visual: { from: 'shell', to: 'shell', action: 'whoami' },
        redLog: { message: 'Running `whoami`. Result: [corp\\j.doe]. Low privileges.', severity: 'Low' },
        blueLog: null,
      },
      {
        step: 2,
        visual: { from: 'shell', to: 'kernel', action: 'Run CVE-202X-XXXX Exploit' },
        redLog: { message: 'T1068: Running local kernel exploit (PrintNightmare).', severity: 'High' },
        blueLog: { message: '**CRITICAL**: EDR: Detected anomalous interaction with Spooler service. Potential PrintNightmare exploit.', severity: 'Critical' },
      },
      {
        step: 3,
        visual: { from: 'kernel', to: 'system_shell', action: 'PrivEsc SUCCESS' },
        redLog: { message: 'Exploit successful. Running `whoami`. Result: [NT AUTHORITY\\SYSTEM].', severity: 'Critical' },
        blueLog: { message: '**CRITICAL**: EDR: [spoolsv.exe] spawned [cmd.exe] with SYSTEM privileges. Host isolation initiated.', severity: 'Critical' },
      },
    ],
  },
  
  // --- 7. DEFENSE EVASION (T1027) ---
  'Defense Evasion': {
    techniqueId: 'T1027',
    techniqueName: 'Obfuscated Files',
    nodes: [
      { id: 'shell', name: 'Attacker (Shell)', type: 'red' },
      { id: 'workstation', name: 'Workstation', type: 'blue' },
      { id: 'edr', name: 'EDR/AV', type: 'neutral' },
    ],
    steps: [
      {
        step: 1,
        visual: { from: 'shell', to: 'workstation', action: 'Download Obfuscated Payload' },
        redLog: { message: 'T1027: Downloading payload packed with custom encoder.', severity: 'Medium' },
        blueLog: null,
      },
      {
        step: 2,
        visual: { from: 'edr', to: 'workstation', action: 'EDR On-Write Scan' },
        redLog: { message: 'Payload written to disk. EDR did not trigger.', severity: 'Medium' },
        blueLog: { message: 'EDR: Scanned new file [payload.exe]. Result: No Threats Found (Signature Miss).', severity: 'Medium' },
      },
      {
        step: 3,
        visual: { from: 'shell', to: 'workstation', action: 'Execute (SUCCESS)' },
        redLog: { message: 'Defense Evasion successful. Payload is running.', severity: 'High' },
        blueLog: { message: '**HIGH**: SIEM: [payload.exe] (unsigned) is making suspicious network calls. (Behavioral Detection).', severity: 'High' },
      },
    ],
  },
  
  // --- 8. CREDENTIAL ACCESS (T1110) ---
  'Credential Access': {
    techniqueId: 'T1110',
    techniqueName: 'Brute Force',
    nodes: [
      { id: 'attacker', name: 'Attacker', type: 'red' },
      { id: 'login', name: 'Login Portal (OWA)', type: 'blue' },
      { id: 'ad', name: 'Active Directory', type: 'neutral' },
    ],
    steps: [
      {
        step: 1,
        visual: { from: 'attacker', to: 'login', action: 'Login Attempt 1 (FAIL)' },
        redLog: { message: 'T1110: Brute force initiated. User [admin], Pass [Password123].', severity: 'Low' },
        blueLog: { message: 'AD: Logon Failure for user [admin] from [Attacker IP].', severity: 'Medium' },
      },
      {
        step: 2,
        visual: { from: 'attacker', to: 'login', action: 'Login Attempt 2 (FAIL)' },
        redLog: { message: 'User [admin], Pass [Spring2024].', severity: 'Low' },
        blueLog: { message: 'AD: Logon Failure for user [admin] from [Attacker IP].', severity: 'Medium' },
      },
      {
        step: 3,
        visual: { from: 'attacker', to: 'login', action: 'Login Attempt 3 (FAIL)' },
        redLog: { message: 'User [admin], Pass [Welcome1].', severity: 'Low' },
        blueLog: { message: '**HIGH**: SIEM: 3+ Logon Failures for [admin] from [Attacker IP]. Brute force suspected.', severity: 'High' },
      },
      {
        step: 4,
        visual: { from: 'attacker', to: 'login', action: 'Login Attempt 4 (FAIL)' },
        redLog: { message: 'User [admin], Pass [Qwerty123].', severity: 'Low' },
        blueLog: { message: 'AD: Account [admin] has been locked due to excessive failed attempts.', severity: 'High' },
      },
      {
        step: 5,
        visual: { from: 'attacker', to: 'login', action: 'Login Attempt 5 (LOCKED)' },
        redLog: { message: 'Attempt failed. Account is locked. Switching targets.', severity: 'Medium' },
        blueLog: { message: 'AD: Logon Failure for user [admin]. Account is locked.', severity: 'High' },
      },
    ],
  },
  
  // --- 9. DISCOVERY (T1083) ---
  'Discovery': {
    techniqueId: 'T1083',
    techniqueName: 'File and Directory Discovery',
    nodes: [
      { id: 'shell', name: 'Attacker (Shell)', type: 'red' },
      { id: 'workstation', name: 'Workstation', type: 'blue' },
      { id: 'fileserver', name: 'File Server', type: 'blue' },
    ],
    steps: [
      {
        step: 1,
        visual: { from: 'shell', to: 'workstation', action: 'Find Local Files' },
        redLog: { message: 'T1083: Running `dir C:\\Users\\*\\Documents\\*.pdf`.', severity: 'Low' },
        blueLog: null,
      },
      {
        step: 2,
        visual: { from: 'shell', to: 'fileserver', action: 'Scan Network Share' },
        redLog: { message: 'T1083: Found network share [\\\\FS-01\\HR]. Scanning for sensitive files.', severity: 'Medium' },
        blueLog: { message: 'SIEM: User [j.doe] accessed high volume of files on [\\\\FS-01\\HR]. (Potential data staging).', severity: 'High' },
      },
    ],
  },
  
  // --- 10. LATERAL MOVEMENT (T1021) ---
  'Lateral Movement': {
    techniqueId: 'T1021',
    techniqueName: 'Remote Services (RDP)',
    nodes: [
      { id: 'shell', name: 'Attacker (WS-01)', type: 'red' },
      { id: 'ws2', name: 'Workstation (WS-02)', type: 'blue' },
      { id: 'dc', name: 'Domain Controller', type: 'neutral' },
    ],
    steps: [
      {
        step: 1,
        visual: { from: 'shell', to: 'dc', action: 'Authenticate (Stolen Creds)' },
        redLog: { message: 'Using stolen credentials for [admin] to authenticate to DC.', severity: 'Medium' },
        blueLog: { message: 'AD: Logon Success for [admin] on [DC-01] from [WS-01].', severity: 'High' },
      },
      {
        step: 2,
        visual: { from: 'shell', to: 'ws2', action: 'T1021: RDP to WS-02' },
        redLog: { message: 'T1021: Moving laterally via RDP to [WS-02] as [admin].', severity: 'High' },
        blueLog: { message: '**HIGH**: EDR: Anomalous RDP connection from [WS-01] to [WS-02] using [admin] account.', severity: 'High' },
      },
    ],
  },

  // --- 11. COLLECTION (T1005) ---
  'Collection': {
    techniqueId: 'T1005',
    techniqueName: 'Data from Local System',
    nodes: [
      { id: 'shell', name: 'Attacker (Shell)', type: 'red' },
      { id: 'workstation', name: 'Workstation', type: 'blue' },
      { id: 'staging', name: 'Staging Dir', type: 'neutral' },
    ],
    steps: [
      {
        step: 1,
        visual: { from: 'shell', to: 'workstation', action: 'Collect User Files' },
        redLog: { message: 'T1005: Collecting .doc, .xls, .pdf from user directories.', severity: 'Medium' },
        blueLog: null,
      },
      {
        step: 2,
        visual: { from: 'workstation', to: 'staging', action: 'T1560: Archive Data (Zip)' },
        redLog: { message: 'T1560: Compressing collected files into [C:\\Windows\\Temp\\data.zip].', severity: 'Medium' },
        blueLog: { message: 'EDR: Suspicious file creation [data.zip] in [C:\\Windows\\Temp].', severity: 'Medium' },
      },
    ],
  },
  
  // --- 12. COMMAND AND CONTROL (T1071) ---
  'Command and Control': {
    techniqueId: 'T1071',
    techniqueName: 'App Layer (DNS Tunnel)',
    nodes: [
      { id: 'agent', name: 'Agent (WS-01)', type: 'blue' },
      { id: 'firewall', name: 'Firewall', type: 'neutral' },
      { id: 'c2', name: 'Attacker C2', type: 'red' },
    ],
    steps: [
      {
        step: 1,
        visual: { from: 'agent', to: 'firewall', action: 'DNS Query (Tunnel)' },
        redLog: { message: 'T1071: Sending C2 data via DNS query (A record) to [cmd.c2-domain.com].', severity: 'Medium' },
        blueLog: { message: 'Firewall: Allowed outbound DNS query (Port 53).', severity: 'Low' },
      },
      {
        step: 2,
        visual: { from: 'firewall', to: 'c2', action: 'DNS Query (Tunnel)' },
        redLog: { message: 'Data successfully tunneled.', severity: 'Medium' },
        blueLog: { message: '**HIGH**: NIDS: DNS Tunneling detected. High volume of DNS requests to [*.c2-domain.com].', severity: 'High' },
      },
    ],
  },

  // --- 13. EXFILTRATION (T1041) ---
  'Exfiltration': {
    techniqueId: 'T1041',
    techniqueName: 'Exfiltration Over C2 Channel',
    nodes: [
      { id: 'staging', name: 'Staging (WS-01)', type: 'blue' },
      { id: 'firewall', name: 'Firewall', type: 'neutral' },
      { id: 'c2', name: 'Attacker C2', type: 'red' },
    ],
    steps: [
      {
        step: 1,
        visual: { from: 'staging', to: 'firewall', action: 'Exfil [data.zip] (Chunk 1)' },
        redLog: { message: 'T1041: Exfiltrating [data.zip] over C2 channel (HTTPS POST).', severity: 'High' },
        blueLog: { message: 'Firewall: Allowed outbound HTTPS (Port 443).', severity: 'Low' },
      },
      {
        step: 2,
        visual: { from: 'staging', to: 'firewall', action: 'Exfil [data.zip] (Chunk 2)' },
        redLog: { message: 'Exfiltration in progress...', severity: 'High' },
        blueLog: { message: '**CRITICAL**: DLP: Data Loss Prevention policy triggered. Detected [data.zip] (100MB) in outbound HTTPS stream.', severity: 'Critical' },
      },
    ],
  },
  
  // --- 14. IMPACT (T1486) ---
  'Impact': {
    techniqueId: 'T1486',
    techniqueName: 'Data Encrypted for Impact',
    nodes: [
      { id: 'shell', name: 'Attacker (Shell)', type: 'red' },
      { id: 'workstation', name: 'Workstation', type: 'blue' },
      { id: 'fileserver', name: 'File Server', type: 'blue' },
    ],
    steps: [
      {
        step: 1,
        visual: { from: 'shell', to: 'workstation', action: 'Deploy Ransomware' },
        redLog: { message: 'T1486: Executing ransomware payload on [WS-01].', severity: 'Critical' },
        blueLog: { message: '**CRITICAL**: EDR: Honeypot file [canary.txt] was modified! Ransomware detected.', severity: 'Critical' },
      },
      {
        step: 2,
        visual: { from: 'shell', to: 'fileserver', action: 'Encrypt Network Shares' },
        redLog: { message: 'T1486: Propagating to network shares. Encrypting [\\\\FS-01\\HR].', severity: 'Critical' },
        blueLog: { message: '**CRITICAL**: EDR: Host [WS-01] quarantined. Network file share access revoked.', severity: 'Critical' },
      },
    ],
  },
};

export const getDefaultScenario = (tactic) => ({
  techniqueId: 'T0000',
  techniqueName: 'Default Action',
  nodes: [
    { id: 'attacker', name: 'Attacker', type: 'red' },
    { id: 'target', name: 'Target System', type: 'blue' },
  ],
  steps: [
    {
      step: 1,
      visual: { from: 'attacker', to: 'target', action: 'Initiate Probe' },
      redLog: { message: `Red Team initiates ${tactic}. Probing.`, severity: 'Low' },
      blueLog: { message: `SIEM correlated 3 low-level events related to [${tactic}].`, severity: 'Low' },
    },
    {
      step: 2,
      visual: { from: 'attacker', to: 'target', action: 'Blocked' },
      redLog: { message: 'Execution failed. Endpoint defense blocked payload.', severity: 'High' },
      blueLog: { message: `DEFENSE RESPONSE: NIDS blocked the payload. ATTACK FAILURE.`, severity: 'Critical' },
    },
  ],
});