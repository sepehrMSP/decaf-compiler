
int main() {
    int t;
    int i;
    string s;
    t = 0;
    s = ReadLine();
	for (i = 1; i < 6; i = i+1){
		if (s[i] == s[i-1]){
		    t = t+1;
		}
		else{
		    t = 0;
		}
		if (t == 6){
		    Print("Yes");
			return 0;
		}
	}
    Print("NO");
}