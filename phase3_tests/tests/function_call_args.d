
void f(int x, int y, bool z, double a){
    if(x == 1 && y == 2 && z == true && a > 2.5){
        Print("ok");
        x = 10;
        y = 100;
        z = false;
        a = 1.5123;
        return;
    }
    Print("not ok");
    return;
}

int main()  {
    int x ;
    bool y;
    double aa;
    x = 1;
    y = true;
    aa = 10.2;
    f(x, 2, y, 10.2);
    Print(x);
    if(y){
        Print("true");
    }
    Print(aa);
}