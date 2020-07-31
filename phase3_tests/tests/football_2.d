
int main() {
    int t;
    int i;
    string s;
    bool found;
    t = 0;
    s = ReadLine();
    found = false;
	for (i = 1; i < 10; i = i+1){
		if (s[i] == s[i-1]){
		    t = t+1;
		}
		else{
		    t = 0;
		}
		if (t == 6){
		    Print("YES");
		    found = true;
		    break;
		}
	}
	if(!found){
        Print("NO");
    }
}