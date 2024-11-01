from generate import generate_spec, generate_seed_generator, generate_code, generate_sub_function, generate_debug, generate_qa

problem = {
    "problem": "There are n types of coins, each with a different value. You want to make a total of k currency units using these coins in any combination. Find the number of ways to achieve this total. You can use any number of each coin.\nCoin combinations with the same composition but in a different order are considered the same.",
    "wrong code": "#include <bits/stdc++.h>\n#include <unordered_map>\n#include <unordered_set>\n\nusing namespace std;\n\nint main() {\n  ios_base::sync_with_stdio(false);\n  cin.tie(NULL);\n  cout.tie(NULL);\n\n  // freopen(\"Input.txt\", \"r\", stdin);\n  int n, k;\n  cin >> n >> k;\n\n  vector<int> vec(n + 1);\n  for (int i = 1; i <= n; ++i)\n    cin >> vec[i];\n\n  vector<int> dp(k + 1, 0);\n  dp[0] = 1;\n\n  for (int i = 1; i <= n; ++i) {\n    for (int j = 1; j <= k; ++j) // j-value\n    {\n      int coin = vec[i];\n      if (coin <= j)\n        dp[j] = dp[j] + dp[j - coin];\n      else\n        dp[j] = dp[j - 1];\n    }\n  }\n\n  cout << dp[k];\n\n  return 0;\n}\n",
    "input": "The first line contains two integers, n and k (1 ≤ n ≤ 100, 1 ≤ k ≤ 10,000). The following n lines each contain the value of a coin. Each coin's value is a natural number not exceeding 100,000.",
    "output": "Output the number of ways to make k currency units. The result will be less than 2^31.",
    "test case input 1": "3 10\n1\n2\n5",
    "test case output 1": "10",
}
formatted_spec = generate_spec(problem)
print(f"formatted spec:\n{formatted_spec}")

code = generate_code(formatted_spec)
print(f"Code:\n{code}")

sub_func = generate_sub_function(code)
print(f"Sub func:\n{sub_func}")

debug_result = generate_debug(sub_func, problem["test case input 1"], problem["test case output 1"])
print(f"Debug:\n{debug_result}")

qa_feedback = generate_qa(formatted_spec, sub_func, debug_result)
print(f"QA: {qa_feedback}")

code = generate_code(code, qa_feedback)
print(code)