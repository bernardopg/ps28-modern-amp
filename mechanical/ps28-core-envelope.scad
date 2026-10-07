// Envelope de estudo, NÃO CAD fabril nem modelo dimensionado do gabinete PS28.
// D-014: mounting points/dissipação OEM são fixos; este retângulo NÃO é o contorno original.
// Master mecânico: original-board-reference.md e manual p.15-18.
// Cotas do fabricante e posições do core B; ver ps28-original-integration.json.
// Não representa furos do plate, woofer, T1, tolerâncias de montagem ou força de clamp.
show_adapter_example = false;
export_for_manufacture = false;
original_plate_measured = false;
assert(!export_for_manufacture || original_plate_measured,
       "BLOQUEADO: faltam plate, furos, contato do dissipador e profundidade medidos");
$fn = 64;
pcb_t = 1.6; // hipótese, stackup não aprovado
module body(center_xy, size_xyz, tone) {
    color(tone) translate([center_xy[0]-size_xyz[0]/2,
                           center_xy[1]-size_xyz[1]/2, pcb_t]) cube(size_xyz);
}
color("darkgreen") cube([145,95,pcb_t]);
body([55,40], [6.1,14,1.2], "black"); // DDV44, NÃO bottom-EP
for (xy=[[91,26.5],[91,57.5]])
    body(xy,[21.8,21.5,14.5],"dimgray"); // HCF2013 max, proxy sem geometria dos leads
for (x=[33.75,57.75]) {
    color("silver") translate([x,15,pcb_t]) cylinder(d=18.5,h=42);
    color([0,1,1,0.25]) translate([x,15,pcb_t+42]) cylinder(d=18.5,h=5);
}
// Ponto de ligação GND interno, não furo existente do gabinete.
color("gold") translate([50,66,pcb_t]) difference() {
    cylinder(d=6.4,h=0.05);cylinder(d=3.2,h=0.1);
}
if (show_adapter_example) {
    // Exemplo de orçamento térmico: direção/span finais dependem do dissipador real.
    color("peru") translate([55-3.8/2,40-6.6/2,pcb_t+1.2]) cube([3.8,6.6,4.8]);
    color([0.72,0.45,0.20,0.7]) translate([55-10,40-3.3,pcb_t+6]) cube([20,23.3,10]);
    echo("Adaptador ilustrativo: NÃO usar para usinagem ou furar plate original");
}
