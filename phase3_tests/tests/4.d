int main(){
    Print("input your name:");
    Print(ReadLine());
    Print("ok bruh now input your age : ->\n", ReadInteger(), "good age? answer is ", true);
    
    if (ReadInteger()){
        Print("ok1 simple if");
    }
    
    if (ReadInteger()){
        Print("wrong");
    }
}
