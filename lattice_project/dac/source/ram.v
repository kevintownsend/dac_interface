module ram(
    input clk,
	input [16:0] adr,
	input [15:0] wr_data,
	input wr_en,
	output [15:0] rd_data);
	
	reg [15:0] ram [72000:0];
	//reg [15:0] ram [66000:0];

	reg [15:0] r_rd_data;
	
	always @(posedge clk) begin
		if(wr_en)
			ram[adr] <= wr_data;
		r_rd_data <= ram[adr];
	end
	assign rd_data = r_rd_data;
	
endmodule