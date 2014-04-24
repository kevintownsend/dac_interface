/* Verilog netlist generated by SCUBA Diamond_1.4_Production (87) */
/* Module Version: 5.2 */
/* C:\lscc\diamond\1.4\ispfpga\bin\nt\scuba.exe -w -n pll_filter -lang verilog -synth synplify -arch ep5c00 -type pll -fin 100 -phase_cntl STATIC -fclkop 100 -fclkop_tol 0.0 -fb_mode CLOCKTREE -noclkos -noclkok -norst -noclkok2 -bw -e  */
/* Wed Jan 30 16:41:33 2013 */


`timescale 1 ns / 1 ps
module pll_filter (CLK, CLKOP, LOCK)/* synthesis syn_noprune=1 */;// exemplar attribute pll_filter dont_touch true 
    input wire CLK;
    output wire CLKOP;
    output wire LOCK;

    wire CLKOP_t;
    wire scuba_vlo;

    VLO scuba_vlo_inst (.Z(scuba_vlo));

    defparam PLLInst_0.FEEDBK_PATH = "CLKOP" ;
    defparam PLLInst_0.CLKOK_BYPASS = "DISABLED" ;
    defparam PLLInst_0.CLKOS_BYPASS = "DISABLED" ;
    defparam PLLInst_0.CLKOP_BYPASS = "DISABLED" ;
    defparam PLLInst_0.CLKOK_INPUT = "CLKOP" ;
    defparam PLLInst_0.DELAY_PWD = "DISABLED" ;
    defparam PLLInst_0.DELAY_VAL = 0 ;
    defparam PLLInst_0.CLKOS_TRIM_DELAY = 0 ;
    defparam PLLInst_0.CLKOS_TRIM_POL = "RISING" ;
    defparam PLLInst_0.CLKOP_TRIM_DELAY = 0 ;
    defparam PLLInst_0.CLKOP_TRIM_POL = "RISING" ;
    defparam PLLInst_0.PHASE_DELAY_CNTL = "STATIC" ;
    defparam PLLInst_0.DUTY = 8 ;
    defparam PLLInst_0.PHASEADJ = "0.0" ;
    defparam PLLInst_0.CLKOK_DIV = 2 ;
    defparam PLLInst_0.CLKOP_DIV = 8 ;
    defparam PLLInst_0.CLKFB_DIV = 1 ;
    defparam PLLInst_0.CLKI_DIV = 1 ;
    defparam PLLInst_0.FIN = "100.000000" ;
    EHXPLLF PLLInst_0 (.CLKI(CLK), .CLKFB(CLKOP_t), .RST(scuba_vlo), .RSTK(scuba_vlo), 
        .WRDEL(scuba_vlo), .DRPAI3(scuba_vlo), .DRPAI2(scuba_vlo), .DRPAI1(scuba_vlo), 
        .DRPAI0(scuba_vlo), .DFPAI3(scuba_vlo), .DFPAI2(scuba_vlo), .DFPAI1(scuba_vlo), 
        .DFPAI0(scuba_vlo), .FDA3(scuba_vlo), .FDA2(scuba_vlo), .FDA1(scuba_vlo), 
        .FDA0(scuba_vlo), .CLKOP(CLKOP_t), .CLKOS(), .CLKOK(), .CLKOK2(), 
        .LOCK(LOCK), .CLKINTFB())
             /* synthesis FREQUENCY_PIN_CLKOP="100.000000" */
             /* synthesis FREQUENCY_PIN_CLKI="100.000000" */
             /* synthesis FREQUENCY_PIN_CLKOK="50.000000" */;

    assign CLKOP = CLKOP_t;


    // exemplar begin
    // exemplar attribute PLLInst_0 FREQUENCY_PIN_CLKOP 100.000000
    // exemplar attribute PLLInst_0 FREQUENCY_PIN_CLKI 100.000000
    // exemplar attribute PLLInst_0 FREQUENCY_PIN_CLKOK 50.000000
    // exemplar end

endmodule
