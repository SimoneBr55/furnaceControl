package Logic;

public class Furnace {
	int status;
	boolean upValve;
	boolean downValve;
	boolean manual;
	long lastDown;
	long lastUp;
	int payload;
	Furnace(){
		this.status = 0; // the furnace starts off
		this.upValve = false; 
		this.downValve = false;
		this.manual = false;
	}

}
