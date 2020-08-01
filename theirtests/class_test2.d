class c{
    void f(int a,int b){
        Print(a,b);
    }
    void g(int a,int b){
        Print(a);
        Print(b);
    }
}

class d extends c{
    void f(int a,int b){
        Print(a);
        Print(2.3);
        Print(b);
    }
}

int main(){
    c obj;
    obj=new d;
    obj.f(5,4);
}