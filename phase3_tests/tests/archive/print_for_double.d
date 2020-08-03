void print(double f){
    int cnt;
    f=f+0.00005;
    cnt=0;
    while(f>=10.0){
        f=f/10.0;
        cnt=cnt+1;
    }
    while(cnt>=0){
        int ragham;
        ragham=0;
        while(f>=1.0){
            ragham=ragham+1;
            f=f-1.0;
        }
        Print(ragham);
        f=f*10.0;
        cnt=cnt-1;
    }
    Print(".");
    for(cnt=0;cnt<4;cnt=cnt+1){
        int ragham;
        ragham=0;
        while(f>=1.0){
            ragham=ragham+1;
            f=f-1.0;
        }
        Print(ragham);
        f=f*10.0;
    }

}

int main() {
    print(123456789.12346);
    Print(123456789.12346);
}
