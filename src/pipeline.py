from generate import generate_spec, generate_code, generate_sub_function, generate_debug, generate_qa
from sanitizer import sanitize

problem = {
    "problem": "The owner of the world-renowned Hyeongtaek Hotel, Kim Hyeongtaek, wants to increase revenue by launching a marketing campaign. A list of cities is given, along with the cost of advertising in each city and the number of hotel customers that would increase as a result. For example, \"In a certain city, spending 9 units of money on advertising brings 3 additional customers.\" The money spent in a city can only be a multiple of the given amount. For instance, spending 9 units to get 3 customers, 18 units to get 6 customers, or 27 units to get 9 customers is allowed. However, spending 3 units to get 1 customer or 12 units to get 4 customers is not allowed. Each city has an unlimited number of potential customers. Write a program to determine the minimum amount of money Hyeongtaek needs to invest to increase the number of customers by at least \(C\).",
    "input": "The first line contains \(C\), the minimum number of customers to increase, and \(N\), the number of cities where Hyeongtaek can advertise. \(C\) is a natural number not exceeding 1,000, and \(N\) is a natural number not exceeding 20. From the second line onward, \(N\) lines provide the cost of advertising in each city and the number of customers gained from that cost. These values are natural numbers not exceeding 100.",
    "output": "Output the answer to the problem on the first line.",
    "test case input": "12 2\n3 5\n 1 1",
    "test case output": "8",
}
wrong_code = """
```cpp
#include<iostream>
#include<algorithm>
#define MAX 21
using namespace std;

int n,c;
int arr[MAX][2];
int dp[1001];

int main(){
    cin >> c >> n;

    for(int i=1;i<=1001;i++){
        dp[i]=99999;    
    }

    int maxP=0;

    for(int i=0;i<n;i++){
        cin >> arr[i][0] >> arr[i][1];
        dp[arr[i][1]]=arr[i][0];
        maxP=max(maxP, arr[i][1]);
    }
    
    int answer=99999;

    for(int i=1;i<=c+maxP;i++){
        for(int j=0;j<n;j++){

            int cost=arr[j][0];
            int people=arr[j][1];

            if(i-people >=0){
                dp[i]=min(dp[i], dp[i-people]+cost);
            }
            
            if(i>=c){
                answer=min(answer,dp[i]);
            }
        }
    }

   cout << answer << "\n";

}
```
"""


formatted_spec = generate_spec(problem)
print(f"formatted spec:\n{formatted_spec}")

wrong_code = generate_code(formatted_spec)
print(f"Wrong Code:\n{wrong_code}")

sub_func = generate_sub_function(wrong_code)
print(f"Sub func:\n{sub_func}")

observed_output = sanitize(sub_func, "./program.cpp", "./program", problem["test case input"],)

debug_result = generate_debug(formatted_spec, sub_func, problem["test case input"], problem["test case output"], observed_output)
print(f"Debug:\n{debug_result}")

qa_feedback = generate_qa(formatted_spec, sub_func, debug_result)
print(f"QA: {qa_feedback}")

code = generate_code(sub_func, qa_feedback)
print(code)