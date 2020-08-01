
class d {
	int a;
	double b;

	int get_a(){
	    return a;
	}

	double get_b(){
	    return b;
	}

	void set_a(int x){
	    a = x;
	}

	void set_b(double y) {
	    b = y;
	}

}


int main() {
	d obj;
	obj = new d;
	obj.set_a(10);
	obj.set_b(2.5);
	Print(obj.get_a());
	Print(obj.get_b());
}