export const tactics = [
  {
    name: 'Reconnaissance',
    techniques: [
      { id: 'T1595', name: 'Active Scanning' },
      { id: 'T1592', name: 'Gather Victim Host Information' },
      { id: 'T1589', name: 'Gather Victim Identity Information' }
    ]
  },
  {
    name: 'Resource Development',
    techniques: [
      { id: 'T1583', name: 'Acquire Infrastructure' },
      { id: 'T1586', name: 'Compromise Accounts' },
      { id: 'T1587', name: 'Develop Capabilities' }
    ]
  },
  {
    name: 'Initial Access',
    techniques: [
      { id: 'T1566', name: 'Phishing' },
      { id: 'T1190', name: 'Exploit Public-Facing Application' },
      { id: 'T1133', name: 'External Remote Services' }
    ]
  },
  {
    name: 'Execution',
    techniques: [
      { id: 'T1059', name: 'Command and Scripting Interpreter' },
      { id: 'T1203', name: 'Exploitation for Client Execution' },
      { id: 'T1204', name: 'User Execution' }
    ]
  },
  {
    name: 'Persistence',
    techniques: [
      { id: 'T1053', name: 'Scheduled Task/Job' },
      { id: 'T1547', name: 'Boot or Logon Autostart Execution' },
      { id: 'T1136', name: 'Create Account' }
    ]
  },
  {
    name: 'Privilege Escalation',
    techniques: [
      { id: 'T1068', name: 'Exploitation for Privilege Escalation' },
      { id: 'T1078', name: 'Valid Accounts' },
      { id: 'T1055', name: 'Process Injection' }
    ]
  },
  {
    name: 'Defense Evasion',
    techniques: [
      { id: 'T1027', name: 'Obfuscated Files or Information' },
      { id: 'T1070', name: 'Indicator Removal' },
      { id: 'T1562', name: 'Impair Defenses' }
    ]
  },
  {
    name: 'Credential Access',
    techniques: [
      { id: 'T1110', name: 'Brute Force' },
      { id: 'T1003', name: 'OS Credential Dumping' },
      { id: 'T1558', name: 'Steal or Forge Kerberos Tickets' }
    ]
  },
  {
    name: 'Discovery',
    techniques: [
      { id: 'T1087', name: 'Account Discovery' },
      { id: 'T1083', name: 'File and Directory Discovery' },
      { id: 'T1046', name: 'Network Service Discovery' }
    ]
  },
  {
    name: 'Lateral Movement',
    techniques: [
      { id: 'T1021', name: 'Remote Services' },
      { id: 'T1091', name: 'Replication Through Removable Media' },
      { id: 'T1080', name: 'Taint Shared Content' }
    ]
  },
  {
    name: 'Collection',
    techniques: [
      { id: 'T1005', name: 'Data from Local System' },
      { id: 'T1560', name: 'Archive Collected Data' },
      { id: 'T1113', name: 'Screen Capture' }
    ]
  },
  {
    name: 'Command and Control',
    techniques: [
      { id: 'T1071', name: 'Application Layer Protocol' },
      { id: 'T1573', name: 'Encrypted Channel' },
      { id: 'T1090', name: 'Proxy' }
    ]
  },
  {
    name: 'Exfiltration',
    techniques: [
      { id: 'T1041', name: 'Exfiltration Over C2 Channel' },
      { id: 'T1048', name: 'Exfiltration Over Alternative Protocol' },
      { id: 'T1567', name: 'Exfiltration Over Web Service' }
    ]
  },
  {
    name: 'Impact',
    techniques: [
      { id: 'T1486', name: 'Data Encrypted for Impact' },
      { id: 'T1485', name: 'Data Destruction' },
      { id: 'T1498', name: 'Network Denial of Service' }
    ]
  }
];

export const blueTeamFindings = [
  { tactic: 'Initial Access', technique: 'T1566: Phishing', severity: 'Critical', measure: 'Email gateway with advanced threat protection enabled' },
  { tactic: 'Initial Access', technique: 'T1190: Exploit Public-Facing Application', severity: 'High', measure: 'Web Application Firewall (WAF) deployed' },
  { tactic: 'Execution', technique: 'T1059: Command and Scripting Interpreter', severity: 'High', measure: 'PowerShell logging and constrained language mode' },
  { tactic: 'Persistence', technique: 'T1053: Scheduled Task/Job', severity: 'Medium', measure: 'Scheduled task monitoring via SIEM' },
  { tactic: 'Privilege Escalation', technique: 'T1068: Exploitation for Privilege Escalation', severity: 'Critical', measure: 'Kernel patch management automated' },
  { tactic: 'Defense Evasion', technique: 'T1027: Obfuscated Files or Information', severity: 'High', measure: 'Endpoint detection analyzing file entropy' },
  { tactic: 'Credential Access', technique: 'T1110: Brute Force', severity: 'High', measure: 'Account lockout policy and MFA enforced' },
  { tactic: 'Discovery', technique: 'T1046: Network Service Discovery', severity: 'Medium', measure: 'Network segmentation and IDS monitoring' },
  { tactic: 'Lateral Movement', technique: 'T1021: Remote Services', severity: 'High', measure: 'Privileged access workstations required' },
  { tactic: 'Collection', technique: 'T1113: Screen Capture', severity: 'Low', measure: 'DLP monitoring for suspicious data access' },
  { tactic: 'Command and Control', technique: 'T1071: Application Layer Protocol', severity: 'Critical', measure: 'DNS sinkholing and proxy inspection' },
  { tactic: 'Exfiltration', technique: 'T1041: Exfiltration Over C2 Channel', severity: 'Critical', measure: 'Egress filtering and data loss prevention' },
  { tactic: 'Impact', technique: 'T1486: Data Encrypted for Impact', severity: 'Critical', measure: 'Immutable backups and EDR ransomware protection' },
  { tactic: 'Reconnaissance', technique: 'T1595: Active Scanning', severity: 'Low', measure: 'Honeypots deployed for early warning' },
  { tactic: 'Execution', technique: 'T1204: User Execution', severity: 'Medium', measure: 'User security awareness training program' },
  { tactic: 'Persistence', technique: 'T1547: Boot or Logon Autostart Execution', severity: 'Medium', measure: 'Registry and startup folder monitoring' },
  { tactic: 'Defense Evasion', technique: 'T1070: Indicator Removal', severity: 'High', measure: 'Centralized logging with tamper protection' },
  { tactic: 'Credential Access', technique: 'T1003: OS Credential Dumping', severity: 'Critical', measure: 'Credential Guard and LSA protection enabled' },
];