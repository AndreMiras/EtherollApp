# README

Updates the balance on roll confirmed and roll processed.
Uses OSC for inter-process communication between roll polling service
and UI.
This requires mainly two new classes, the OscAppServer and OscAppClient.
The OSC app client connects to the OSC app server to communicate with
the application.
MonitorRollsService -> OscAppClient -> OscAppServer -> App
