/*
	Copyright (C) 2014 Ryosuke Fukatani All Rights Reserved
	
    This file is part of pylink.

    pylink is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.

    pylink is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with pylink.  If not, see <http://www.gnu.org/licenses/>.
*/

module top;
   int ret;//return from python time driven simulator 1 or -1.
   bit CLK,RST,AD_OUT;
   
   sinc_filter sinc (.*);
   
   export "DPI-C" task v_task;
   task v_task(input int i, output int o);
      #100;
      $display("Call verilog task.");
   endtask // verilog_task
   import "DPI-C" context task py_exe(input int a, output int o);
   import "DPI-C" context task py_func(string func_name);
   import "DPI-C" context task py_start(input real time_step, input int divide_num);
   import "DPI-C" context task py_end();

      initial begin
         py_start(0.005,8);
         RST=1'b1;
         #10;
         RST=1'b0;
         CLK=1'b0;
         
         for(int i=0;i<3000;i++) begin
            #10;
            CLK=1'b0;
            py_exe(sinc.dif3, ret);
            if(ret > 0)
              AD_OUT=1'b1;
            else
              AD_OUT=1'b0;
            
            #10;
            CLK=1'b1;
            //$display("ret=%f", ret);
         end
         
         //py_func("sim_end");
         py_end();
      end
endmodule // top

module sinc_filter(CLK,RST,AD_OUT);
  input CLK;
  input RST;
  input AD_OUT;
  
  logic signed [19:0] integ1,integ2,integ3;
  logic signed [19:0] dif1,dif2,dif3;
  logic [3:0] count;
  
  always @(posedge CLK or negedge RST) begin
     if(RST) begin
        integ1 <= 20'sd0;
        integ2 <= 20'sd0;
        integ3 <= 20'sd0;
     end else begin
        integ1 <= (AD_OUT) ? 20'sd1 : -20'sd1;
        integ2 <= integ2 + integ1;
        integ3 <= integ3 + integ2;
     end
  end
  
  always @(posedge CLK or negedge RST) begin
     if(RST) begin
        dif1 <= 20'sd0;
        dif2 <= 20'sd0;
        dif3 <= 20'sd0;
     end else if(count == 4'd15) begin
        dif1 <= integ3;
        dif2 <= integ3 - dif1;
        dif3 <= integ3 - dif1 - dif2;
     end else begin
        dif1 <= dif1;
        dif2 <= dif2;
        dif3 <= dif3;
     end
  end
  
  always @(posedge CLK or negedge RST) begin
     if(RST)
       count <= 4'd0;
     else
       count <= count + 4'd1;
  end
  
  
endmodule