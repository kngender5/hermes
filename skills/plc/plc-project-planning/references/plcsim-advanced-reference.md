# S7-PLCSIM Advanced — Quick Reference

## Components

| Component | File | Purpose |
|-----------|------|---------|
| Runtime Manager | `Siemens.Simatic.Simulation.Runtime.Manager.exe` | Background process managing all instances. Auto-starts when API is first used. |
| Runtime Instance | `Siemens.Simatic.Simulation.Runtime.Instance.exe` | Per-PLC process. Loads virtual controller firmware. One per instance. |
| API Library (64-bit) | `Siemens.Simatic.Simulation.Runtime.Api.x64.dll` | .NET API for C# co-simulation. Located in `C:\Program Files (x86)\Common Files\Siemens\PLCSIMADV\API\` |

## TIA Settings for Simulation

In TIA Portal:
1. CPU Properties → Protection → "Enable simulation support" = ON
2. For download: PG/PC Interface = `PLCSIM.TCPIP.1`
3. Start Search → select simulated CPU → Load → RUN

## Network Modes

| Mode | Communication | Use Case |
|------|--------------|----------|
| Softbus | Internal virtual bus | Single PC, no real network needed |
| TCPIO | Real TCP/IP stack | HMI connection, multi-PLC, external tools |

## API Key Functions (C#)

```csharp
// Register instance
instance = SimulationRuntimeManager.RegisterInstance(ECPUType.CPU1500_SW_OC_Unspecified, "InstanceName");

// Power & Mode
instance.PowerOn(60000);   // Start virtual PLC
instance.PowerOff(6000);   // Shut down
instance.Run(6000);        // Go to RUN
instance.Stop(6000);       // Go to STOP

// Network
instance.SetIPSuite(0, new SIPSuite4("192.168.0.20", "255.255.255.0", "0.0.0.0"), true);

// I/O Access
instance.UpdateTagList(ETagListDetails.IO);           // Sync tag list
bool val = instance.ReadBool("TagName");               // Read by name
instance.WriteBool("TagName", true);                   // Write by name

// Events (must be registered)
instance.IsSendSyncEventInDefaultModeEnabled = true;
instance.OnSyncPointReached += OnSyncPoint;           // Fired at end of each PLC cycle
instance.OnSoftwareConfigurationChanged += OnConfigChanged;  // Fired when program changes

// Cleanup
SimulationRuntimeManager.UnregisterInstance(instanceName);
```

## Virtual Time Scaling

- Default: 1.0x (real-time)
- Range: 0.1x (10x slower) to 10x+ (fast forward)
- Useful for: timer testing, long-duration simulations
- Set in PLCSIM UI → Virtual Time Scaling dropdown

## Co-Simulation Architecture

```
C# Application
    ↓ OnSyncPointReached (every PLC cycle)
    ↓ Read PLC outputs (actuator states)
    ↓ Run plant simulation step
    ↑ Write PLC inputs (sensor states)
    ↑
PLCSIM Advanced Runtime Manager
    ↑
Virtual PLC Instance (runs actual PLC OB/FC/FB/DB)
```

## Siemens Documentation Files (Entry ID 109739660)

Located in `C:\Users\rkarl\OneDrive\Dokumenter\Siemens TIA\documents\`:

| File | Content |
|------|---------|
| `109739660_PLCSIM_ADV_GettingStarted_v1.0.2.pdf` | Complete walkthrough (68 pages) |
| `Readme_S7-PLCSIM_V19UPD1_enUS.pdf` | Known issues, OS support |
| `109739660_PLCSIM_ADV_COSIM_APPL_V1_0_2.zip` | C# co-simulation VS2022 project |
| `109739660_PLCSIM_ADV_Display_1.0.2.zip` | HMI display simulator (rarely needed) |

Online manuals:
- Function manual: https://support.industry.siemens.com/cs/document/109977691
- API manual: https://support.industry.siemens.com/cs/document/109977690

## Differences: PLCSIM V20 vs PLCSIM Advanced V7.0

| Feature | PLCSIM V20 | PLCSIM Advanced V7.0 |
|---------|-----------|---------------------|
| License | Included with TIA | Separate license |
| Network | No real IP stack | Full TCP/IP (Softbus + real) |
| HMI connect | Limited | Full WinCC Unified via TCP/IP |
| Max instances | Limited | Up to 16 |
| API access | None | C/C++ and C# .NET API |
| Co-simulation | No | Yes (via Runtime API) |
| OPC UA/Modbus | No | Yes (between virtual PLCs) |
| Virtual time | Yes | Yes |

## Common PLCSIM Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| Download fails with NTP error | NTP time sync enabled in CPU config | Disable NTP in device configuration |
| Timeout on large arrays | HMI-visible arrays create thousands of tags | Reduce array size or split |
| Instance not found | PLCSIM Advanced not running | Start PLCSIM Advanced or PLCSIM V20 UI first |
| Softbus communication fails | Network mode mismatch | Set `ENetworkMode.Softbus` in API or select Softbus in UI |

## Recommended Test Sequence for Warehouse Projects

1. I/O Check — SIM tables: toggle every input, verify every output
2. Safety Circuit — E-stop → all stop; door → alarm; reset → recover
3. Single Cycle — One pallet through full sequence
4. All Sizes — Small/medium/large routing to correct floor
5. Floor Full — Alarm triggers, no more pallets to full floor
6. Lift Timeout — Alarm triggers, requires manual reset
7. Continuous Run — Multiple pallets (time scale 2x+), no deadlocks
8. HMI Integration — PLCSIM Advanced + WinCC Unified screens
9. Error Injection — Co-simulation: sensor fault → alarm → ack → resume
