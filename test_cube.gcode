;FLAVOR:Marlin
;TIME:1200
;Filament used: 2.5m
;Layer height: 0.2
;MINX:10
;MINY:10
;MINZ:0.2
;MAXX:40
;MAXY:40
;MAXZ:30
;Generated with FakeSlicer

; --- Slicer Settings for Impact Prognosticator ---
; infill_percentage = 40
; wall_line_count = 4
; layer_height = 0.2
; infill_pattern = GYROID
; --- End Slicer Settings ---

G28 ; Home all axes
G90 ; Use absolute positioning
G1 Z5 F5000 ; Lift nozzle

; A few fake printing moves
G1 X10 Y10 Z0.2 F3000 ; Move to start
G1 X40 Y10 E15 F1500 ; Draw a line
G1 X40 Y40 E30 ; Draw another line
G1 X10 Y40 E45 ; Draw a third line
G1 X10 Y10 E60 ; Complete the square

G1 Z30 ; Move Z up
M104 S0 ; Turn off temperature
M107 ; Turn off fan
M84 ; Disable motors
