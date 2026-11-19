/*
 XWiz Audio // Cyberpunk V1 | Logitech S120 driver reuse
 Author: OpenAI, 2026-11-17
 IMPORTANT: The shells are for speaker DRIVERS and speaker-level wires only.
 Do not put the S120's exposed mains AC transformer / PSU in these printed housings.
 The nominal 2-inch speakers have variable mounting geometries. Measure before final assembly.

 How to export: change 'part' or use `openscad -D 'part="shell"' -o shell.stl file.scad`
 Parts: shell (2x), driver_plate (2x), rear_panel (2x), left_rail (2x), right_rail (2x), badge (2x), brow (2x), test_plate (1x optional).
 All measurements in mm. No supports needed for components printed in their native flat orientations.
*/

$fn = 64;
part = "assembly";  // [assembly, shell, driver_plate, rear_panel, left_rail, right_rail, badge, brow, test_plate]

// -- Parametric fit controls --
body_width = 110;
body_height = 166;
body_depth = 90;
wall = 3.2;
front_wall = 5.2;
body_chamfer = 14;
driver_y = 22;

// Update these AFTER measuring the real Logitech speaker driver
speaker_cutout = 46;           // hole behind the cone/basket. Measure required clearance.
driver_screw_d = 3.1;          // through-hole in replaceable driver plate
driver_slot_inner_radius = 27; // radial adjustment area (nominal)
driver_slot_outer_radius = 34;

// Fixed interface between shell and replaceable driver plate
plate_width = 89;
plate_height = 89;
plate_corner = 9;
plate_thickness = 4.5;
plate_recess_depth = 0;        // plate surface-mounts: no unsupported pocket/bridge
plate_body_opening = 73;
plate_bolt_x = 36;
plate_bolt_y = 36;

// Rear panel and fastener bosses
rear_thickness = 3.6;
back_bolt_x = 40;
back_bolt_y = 66;
rear_screw_d = 2.7;  // pilot for self tapping M3; test against your fasteners

module chamfer_box_2d(w,h,c) {
    polygon(points=[[-w/2+c,-h/2],[w/2-c,-h/2],[w/2,-h/2+c],
    [w/2,h/2-c],[w/2-c,h/2],[-w/2+c,h/2],[-w/2,h/2-c],[-w/2,-h/2+c]]);
}
module near_flat_slot(r0,r1,d,ang) {
    hull() {
        translate([r0*cos(ang),r0*sin(ang),-1]) cylinder(d=d,h=plate_thickness+2);
        translate([r1*cos(ang),r1*sin(ang),-1]) cylinder(d=d,h=plate_thickness+2);
    }
}

// Body shell with boss ribs fused through supports, and correctly preserved inside the hollow.
// Subtractions in the main cavity above also remove standalone bosses unless reintroduced.
// Rebuild with explicit union of hollow-shell, front posts, and rear reinforced posts.
module shell_complete() {
    difference() {
        union() {
            difference() {
                linear_extrude(body_depth) chamfer_box_2d(body_width,body_height,body_chamfer);
                translate([0,0,front_wall]) linear_extrude(body_depth-front_wall+0.5)
                    chamfer_box_2d(body_width-2*wall,body_height-2*wall,body_chamfer-wall);
            }
            for (x=[-plate_bolt_x,plate_bolt_x]) for(y=[-plate_bolt_y,plate_bolt_y]) {
                translate([x,driver_y+y,front_wall-0.01]) cylinder(d=12,h=17);
            }
            for(x=[-back_bolt_x,back_bolt_x]) for(y=[-back_bolt_y,back_bolt_y]) {
                translate([x,y,front_wall-0.01]) cylinder(d=12.4,h=body_depth-front_wall+0.01);
                // Horizontal stem from the boss to its adjacent sidewall
                translate([x>0?x:x-12,y-4,front_wall-0.01]) cube([12,8,body_depth-front_wall+0.01]);
            }
        }
        // Circular clearance through front; adapter sits flush AGAINST the outer face.
        // No recessed pocket, avoiding long unsupported bridges during printing.
        translate([0,driver_y,-1]) cylinder(d=plate_body_opening,h=front_wall+2);
        // M3 self-tapping screw pilot holes (adapter attaches to integrated face bosses)
        for(x=[-plate_bolt_x,plate_bolt_x]) for(y=[-plate_bolt_y,plate_bolt_y])
            translate([x,driver_y+y,-1]) cylinder(d=2.7,h=front_wall+17);
        for(x=[-back_bolt_x,back_bolt_x]) for(y=[-back_bolt_y,back_bolt_y])
            translate([x,y,body_depth-15.5]) cylinder(d=rear_screw_d,h=17);
    }
}

module driver_plate() {
    difference() {
        linear_extrude(plate_thickness) chamfer_box_2d(plate_width,plate_height,plate_corner);
        translate([0,0,-1]) cylinder(d=speaker_cutout,h=plate_thickness+2);
        for (a=[45,135,225,315]) near_flat_slot(driver_slot_inner_radius,driver_slot_outer_radius,driver_screw_d,a);
        // 4 attachment holes align with fixed posts in shell
        for (x=[-plate_bolt_x,plate_bolt_x]) for(y=[-plate_bolt_y,plate_bolt_y])
            translate([x,y,-1]) cylinder(d=3.3,h=plate_thickness+2);
    }
}

module rear_panel() {
    difference() {
        linear_extrude(rear_thickness) chamfer_box_2d(body_width,body_height,body_chamfer);
        for(x=[-back_bolt_x,back_bolt_x]) for(y=[-back_bolt_y,back_bolt_y]) {
            translate([x,y,-1]) cylinder(d=3.4,h=rear_thickness+2);
            // Shallow counterbore on the external face; optional for M3 pan-head screws
            translate([x,y,rear_thickness-1.0]) cylinder(d=6.4,h=2);
        }
        // Speaker-level wire exit ONLY, not an AC power cable inlet
        translate([0,-56,-1]) cylinder(d=6.5,h=rear_thickness+2);
    }
}

module rail(right=1) {
    // Thin polygon in a second contrasting filament, glued to face edges.
    mirror([right==1 ? 0 : 1,0,0]) linear_extrude(1.8)
      polygon(points=[[47,-67],[51,-63],[51,-34],[48,-27],
       [51,-20],[51,42],[47,52],[47,64],[54,57],[54,-61]]);
}
module badge() {
    // Separate front label. Text is raised to permit an AMS layer-color swap.
    union() {
        linear_extrude(2.4) chamfer_box_2d(78,25,5);
        translate([0,1,2.4]) linear_extrude(0.7)
            text("XWIZ // 01",size=8.4,font="Liberation Sans:style=Bold",halign="center",valign="center",spacing=1.0);
        translate([0,-8,2.4]) linear_extrude(0.5)
            text("AUDIO SYSTEM",size=3.8,font="Liberation Sans:style=Bold",halign="center",valign="center");
    }
}
module brow() {
    linear_extrude(1.8) polygon(points=[[-30,-2],[-21,2],[21,2],[30,-2],[19,-1],[-19,-1]]);
}
module test_plate() {
    // Full-size driver plate: print one inexpensive test before printing two shells.
    driver_plate();
}

if (part == "shell") shell_complete();
else if (part == "driver_plate") driver_plate();
else if (part == "rear_panel") rear_panel();
else if (part == "left_rail") rail(-1);
else if (part == "right_rail") rail(1);
else if (part == "badge") badge();
else if (part == "brow") brow();
else if (part == "test_plate") test_plate();
else if (part == "assembly") {
    color("#515d70") shell_complete();
    color("#909aa3") translate([0,driver_y,-plate_thickness]) driver_plate();
    color("#515d70") translate([0,0,body_depth]) rear_panel();
    color("#24fcd4") translate([0,0,-2.0]) rail(-1);
    color("#24fcd4") translate([0,0,-2.0]) rail(1);
    color("#c7e515") translate([0,-50,0]) rotate([0,180,0]) badge();
    color("#24fcd4") translate([0,75,-2]) brow();
}
