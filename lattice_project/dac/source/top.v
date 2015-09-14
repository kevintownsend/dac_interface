`timescale 1ns / 1 ps
//choose PLL or no PLL
//`define USE_PLL
//CLK_FPGA_IN_1:B18 CLK_FPGA_IN_2:A19
module top (
	rstn,
	clk,
	led0,
	led1,
	led2,
	
	rst_in_n,
	en_in_n,
	clk_calin_n,
	adr,
	//oe_cal_n,
	clk_in_fpga,
	clk_out_fpga,
	//clk_sel,
	//oe_norm_n,
	d_in,
	//d_x,
	//out_comp,
	//ctrl,
	//send,
	uart_in,
	uart_out);
	
input rstn, clk;
output led0, led1, led2;
output rst_in_n, en_in_n, clk_calin_n;
output [2:0] adr;
wire oe_cal_n;
input clk_in_fpga;
output clk_out_fpga;
//input clk_sel;
wire oe_norm_n;
output [14:0] d_in;
wire d_x;
//input out_comp;
//output ctrl;
//output send;

input uart_in;
output uart_out;

reg r_led2;
reg [27:0] counter;


reg [4:0] state, next_state;
`define IDLE		'D0
`define LOAD_DATA	'D1
`define LOAD_ADR	'D2
`define AUTO_COMP	'D3
`define LOAD_MEM	'D4
`define NORM_MODE	'D5
`define LOAD_ADR1	'D6
`define LD_HI_DATA	'D7
`define LD_STATUS	'D8
`define LD_DAT_CNT 	'D9
`define LD_RAM_END 	'D10
`define LD_1RAM1	'D11
`define LD_1RAM2	'D12
`define RD_1RAM		'D13
`define LD_DAT_CNT2	'D14
`define LD_RAM_END2	'D15
`define RD_2RAM2	'D16
`define RD_DAT_CNT	'D17
`define RD_DAT_CNT2	'D18
`define LD_DIV_CLK	'D19
`define LD_DIV_CLK2	'D20
`define LD_DIV_CLK3	'D21
`define LD_DIV_CLK4	'D22
`define LD_DAT_CNT3	'D23
`define LD_DAT_CNT4	'D24
`define LD_RAM_END3	'D25
`define LD_RAM_END4	'D26
//TODO: add states to test ram

reg [14:0] data, next_data;
reg [2:0] buf_adr_next, buf_adr;
reg buf_clk_calin_n_next, buf_clk_calin_n;
reg [31:0] data_count, next_data_count;
reg [31:0] data_size, next_data_size;
reg [15:0] scratch, next_scratch;
reg e_o, next_e_o;
wire [14:0] norm_rd_data;

reg norm_wr_en, next_norm_wr_en;

wire external_clk_en;
wire norm_mode_clk_sel; //, next_norm_mode_clk_sel;
reg norm_mode_div_clk, next_norm_mode_div_clk;
reg norm_mode_extern_clk, next_norm_mode_extern_clk;
wire norm_clk;
reg [31:0] div_clk_count;
reg [31:0] div_clk_divider, next_div_clk_divider;
reg div_clk;
always @(posedge clk)
	if(~|div_clk_count) 
		div_clk = !div_clk;
		
always @(posedge clk)
	if(div_clk_count >= div_clk_divider)
		div_clk_count <= 0;
	else
		div_clk_count <= div_clk_count + 1;

reg [7:0] status, next_status;
assign rst_in_n = status[0];
assign en_in_n = status[1];
assign external_clk_en = status[2];
assign norm_mode_clk_sel = status[3];

assign oe_cal_n = 0;
reg clk_out_fpga_prime;
reg clk_out_en;

`ifdef USE_PLL
	wire ddr_clkout;
	ddr1 ddr_clk(.clk(norm_clk), .da(1), .db(0), .clkout(ddr_clkout), .q(clk_out_fpga));
`else
	assign clk_out_fpga = clk_out_fpga_prime;
`endif

reg [9:0] default_clk_out_div;
wire default_clk_out;

always @(posedge clk) begin
	default_clk_out_div <= default_clk_out_div + 1;
end
assign default_clk_out = default_clk_out_div[9];


always @* begin
	if(state == `NORM_MODE) begin
		clk_out_fpga_prime = norm_clk;
		clk_out_en = 1;
	end else begin
		clk_out_fpga_prime = default_clk_out;
		clk_out_en = 0;
	end
end
assign oe_norm_n = 0;
//assign d_in = data;
//assign d_x = 0;
//assign ctrl = 0;
//assign send = 0;
assign adr = buf_adr;
assign clk_calin_n = buf_clk_calin_n;
/*
always @*
	if(norm_mode_div_clk)
		norm_clk = div_clk;
	else
		norm_clk = clk;
*/
reg norm_clk_mid;
/*
DCS dcs1(
	.CLK1(div_clk),
	.CLK0(clk_in_fpga),
	.SEL(norm_mode_div_clk),
	.DCSOUT(norm_clk_mid));
*/
always @* begin
	if(norm_mode_div_clk)
		norm_clk_mid = div_clk;
	else
		norm_clk_mid = clk_in_fpga;
end

wire norm_clk_mid_buf;
/*
clk_div_pll clk_div_pll_inst(
	.CLK(norm_clk_mid),
	.CLKOP(norm_clk_mid_buf),
	.LOCK());
*/

`ifdef USE_PLL
pll_filter pll_filter_inst(
	.CLK(clk),
	.CLKOP(norm_clk));
`else
DCS dcs2(
	.CLK1(norm_clk_mid),
	.CLK0(clk),
	.SEL(norm_mode_extern_clk),
	.DCSOUT(norm_clk));
`endif


always @(posedge clk) begin
	if(state == `NORM_MODE) begin
		if(norm_mode_clk_sel) begin
			norm_mode_div_clk <= 1;
			norm_mode_extern_clk <= 1;
		end else if(external_clk_en) begin
			norm_mode_div_clk <= 0;
			norm_mode_extern_clk <= 1;
		end else begin
			norm_mode_div_clk <= 1;
			norm_mode_extern_clk <= 0;
		end
	end else begin
		norm_mode_div_clk <= 1;
		norm_mode_extern_clk <= 0;
	end
	//norm_mode_div_clk <= 0; //testing
end

wire new_rx_data;
wire [7:0] rx_data;
wire test_clk, test_out;
reg [7:0] tx_data, next_tx_data;
reg new_tx_data, next_new_tx_data;
wire tx_busy;
	
sdr_15bit sdr_data(
	.clk(!norm_clk),
	.clkout(), //TODO: add clk out
	.reset(!rstn),
	.d(data),
	.dout(d_in));
	
//assign clk_out_fpga = test_clk;
assign d_x = 0;
//set for 9600 baud
//	.baud_freq(12'H18),
//	.baud_limit(16'H3CF1),
//set for 115200
uart_top uart_block(
	.clock(clk),
	.reset(!rstn),
	.ser_in(uart_in),
	.ser_out(uart_out),
	.rx_data(rx_data),
	.new_rx_data(new_rx_data),
	.tx_data(tx_data),
	.new_tx_data(new_tx_data),
	.tx_busy(tx_busy),
	.baud_freq(12'H120),
	.baud_limit(16'H3D09),
	.baud_clk());

always @(posedge clk or negedge rstn) begin
	if (!rstn) begin
		counter <= 0;
		r_led2 <= 1;
	end
	else begin
		counter <= counter + 1;
		r_led2 <= 0;
	end
end
assign led2 = r_led2;
//assign led0 = counter[27];
assign led0 = data[0];
assign led1 = counter[10];

//state combinational logic
always @* begin
	next_state = state;
	buf_adr_next = buf_adr;
	buf_clk_calin_n_next = buf_clk_calin_n;
	next_data_count = data_count;
	next_scratch = scratch;
	next_e_o = e_o;
	next_data = data;
	next_norm_wr_en = 0;
	next_status = status;
	next_data_size = data_size;
	next_new_tx_data = 0;
	next_tx_data = 0;
	next_div_clk_divider = div_clk_divider;
	case(state)
		`IDLE: begin
			if(new_rx_data)
				next_state = rx_data[4:0];
			next_e_o = 0;
		end
		`LOAD_DATA: begin		
			if(new_rx_data) begin
				next_state = `LD_HI_DATA;
				next_data[7:0] = rx_data;
			end
		end
		`LD_HI_DATA: begin
			if(new_rx_data) begin
				next_state = `IDLE;
				next_data[14:8] = rx_data;
			end
		end
		`LOAD_ADR: begin
			buf_clk_calin_n_next = 1;
			if(new_rx_data) begin
				buf_adr_next = rx_data[2:0];
				next_state = `LOAD_ADR1;
			end
		end
		`AUTO_COMP: begin //TODO: later
			next_state = `IDLE;
		end
		`LOAD_MEM: begin
			if(new_rx_data) begin
				if(e_o) begin
					next_scratch[14:8] = rx_data[6:0];
					next_norm_wr_en = 1;
					//load to ram and inc counter
					next_data_count = data_count + 1;
					next_e_o = 0;
				end else begin
					next_scratch[7:0] = rx_data;
					next_e_o = 1;
					//load to scratch
				end
			end
			if(data_count == 11'b10000000000) begin
				//if counter full return
				//TODO: send finish signal
				next_state = `IDLE;
			end else begin
				next_state = `LOAD_MEM;
			end

		end
		`NORM_MODE: begin
			next_data = norm_rd_data[14:0];
			next_data_count = data_count + 1;
			if(data_count == data_size) begin
				next_data_count = 0;
			end
			if(new_rx_data)
				next_state = `IDLE;
		end
		`LOAD_ADR1: begin
			buf_clk_calin_n_next = 0;
			next_state = `IDLE;
		end
		`LD_STATUS: begin
			if(new_rx_data) begin
				next_state = `IDLE;
				next_status = rx_data;
			end else
				next_state = `LD_STATUS;
		end
		`LD_DAT_CNT: begin
			if(new_rx_data) begin
				next_state = `LD_DAT_CNT2;
				next_data_count[7:0] = rx_data;
			end
		end
		`LD_DAT_CNT2: begin
			if(new_rx_data) begin
				next_state = `LD_DAT_CNT3;
				next_data_count[15:8] = rx_data[7:0];
			end
		end
		`LD_DAT_CNT3: begin
			if(new_rx_data) begin
				next_state = `LD_DAT_CNT4;
				next_data_count[23:16] = rx_data[7:0];
			end
		end
		`LD_DAT_CNT4: begin
			if(new_rx_data) begin
				next_state = `IDLE;
				next_data_count[31:24] = rx_data[7:0];
			end
		end
		`LD_RAM_END: begin
			if(new_rx_data) begin
				next_state = `LD_RAM_END2;
				next_data_size[7:0] = rx_data;
			end
		end
		`LD_RAM_END2: begin
			if(new_rx_data) begin
				next_state = `LD_RAM_END3;
				next_data_size[15:8] = rx_data[7:0];
			end
		end
		`LD_RAM_END3: begin
			if(new_rx_data) begin
				next_state = `LD_RAM_END4;
				next_data_size[23:16] = rx_data[7:0];
			end
		end
		`LD_RAM_END4: begin
			if(new_rx_data) begin
				next_state = `IDLE;
				next_data_size[31:24] = rx_data[7:0];
			end
		end
		`LD_1RAM1: begin
			if(new_rx_data) begin
				next_state = `LD_1RAM2;
				next_scratch[7:0] = rx_data;
			end
		end
		`LD_1RAM2: begin
			if(new_rx_data) begin
				next_state = `IDLE;
				next_scratch[15:8] = rx_data;
				next_norm_wr_en = 1;
			end
		end
		`RD_1RAM: begin
			next_data = norm_rd_data;
			next_state = `IDLE;
		end
		`RD_DAT_CNT:begin
			if(!tx_busy)begin
				next_state = `RD_DAT_CNT2;
				next_new_tx_data = 1;
				next_tx_data = data_count[7:0];
			end
		end
		`RD_DAT_CNT2:begin
			if(!tx_busy)begin
				next_state = `IDLE;
				next_new_tx_data = 1;
				next_tx_data[6:0] = data_count[14:8];
			end			
		end
		`LD_DIV_CLK:begin
			if(new_rx_data) begin
				next_state = `LD_DIV_CLK2;
				next_div_clk_divider[7:0] = rx_data;
			end
		end
		`LD_DIV_CLK2:begin
			if(new_rx_data) begin
				next_state = `LD_DIV_CLK3;
				next_div_clk_divider[15:8] = rx_data;
			end
		end
		`LD_DIV_CLK3:begin
			if(new_rx_data) begin
				next_state = `LD_DIV_CLK4;
				next_div_clk_divider[23:16] = rx_data;
			end
		end
		`LD_DIV_CLK4:begin
			if(new_rx_data) begin
				next_state = `IDLE;
				next_div_clk_divider[31:24] = rx_data;
			end
		end
//TODO: add extra states where needed eg manual compare
		default: next_state = `IDLE;
	endcase
end

//state register logic
always @(posedge clk or negedge rstn) begin
	if (!rstn) begin
		 state <= `IDLE;
		 //data_count <= 0;
		 scratch <= 0;
		 e_o <= 0;
		 //data <= 0;
		 norm_wr_en <= 0;
		status <= 8'b00000011;
		data_size <= 0;
		tx_data <= 0;
		new_tx_data <= 0;
		div_clk_divider <= 0;
	end
	else begin
		data_size <= next_data_size;
		state <= next_state;
		//data_count <= next_data_count;
		scratch <= next_scratch;
		e_o <= next_e_o;
		//data <= next_data;
		norm_wr_en <= next_norm_wr_en;
		status <= next_status;
		new_tx_data <= next_new_tx_data;
		tx_data <= next_tx_data;
		div_clk_divider <= next_div_clk_divider;
	end
end

always @(posedge norm_clk or negedge rstn) begin
	if(!rstn) begin
		data_count <= 0;
		data <= 0;
	end else begin
		data_count <= next_data_count;
		data <= next_data;
	end
end

//output
always @(posedge clk) begin
	buf_clk_calin_n <= buf_clk_calin_n_next;
	buf_adr <= buf_adr_next;
end

wire rd_data_extra;
//ram for normal mode
ram norm_ram(
	.clk(norm_clk),
	.adr(data_count[16:0]),
	.wr_data(scratch),
	.wr_en(norm_wr_en),
	.rd_data({rd_data_extra, norm_rd_data}));

endmodule