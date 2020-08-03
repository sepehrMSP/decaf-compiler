int main(){

    int i;
    int j;
    string [][] s;

    s = NewArray(3, string[]);
    s[0] = NewArray(2, string);
    s[1] = NewArray(2, string);
    s[2] = NewArray(2, string);

    s[0][0] = "a00";
    s[0][1] = "a01";
    s[1][0] = "a10";
    s[1][0] = "a10";
    s[1][1] = "a11";
    s[2][0] = "a20";
    s[2][1] = "a21";
    for(i=0; i < 3; i = i+1){
        for(j=0; j < 2; j = j+1){
            Print(s[i][j]);
        }
    }

    s[1][1] = s[0][0];
    s[0][0] = "sbc";
    Print(s[1][1]);
    Print(s[0][0]);
}