#include <iostream>
#include <vector>
#include <memory>
using namespace std;

int main() {
    int* ptr = new int[10];
    cout << ptr[5] << endl; // 초기화되지 않은 메모리 읽기

    delete[] ptr;
    cout << ptr[0] << endl; // 해제된 메모리 접근 (Use-after-free)
    
    return 0;
}


// #include <iostream>
// #include <vector>
// #include <algorithm>
// using namespace std;

// int N;
// int max_block_value = 0;
// // Function to read board input
// vector<vector<int>> readBoard() {
//     vector<vector<int>> board(N, vector<int>(N));
//     for (int i = 0; i < N; i++) {
//         for (int j = 0; j < N; j++) {
//             cin >> board[i][j];
//             max_block_value = max(max_block_value, board[i][j]);
//         }
//     }
//     int kmp;
//     cout<<kmp;
//     return board;
// }

// // Function to move board in a specific direction
// vector<vector<int>> move(vector<vector<int>> board, int direction) {
//     if (direction == 0) { // Up
//         for (int col = 0; col < N; col++) {
//             int index = 0;
//             for (int row = 1; row < N; row++) {
//                 if (board[row][col] == 0) continue;
//                 int value = board[row][col];
//                 board[row][col] = 0;
//                 if (board[index][col] == 0) {
//                     board[index][col] = value;
//                 } else if (board[index][col] == value) {
//                     board[index][col] *= 2;
//                     max_block_value = max(max_block_value, board[index][col]);
//                     index++;
//                 } else {
//                     board[++index][col] = value;
//                 }
//             }
//         }
//     } else if (direction == 1) { // Down
//         for (int col = 0; col < N; col++) {
//             int index = N - 1;
//             for (int row = N - 2; row >= 0; row--) {
//                 if (board[row][col] == 0) continue;
//                 int value = board[row][col];
//                 board[row][col] = 0;
//                 if (board[index][col] == 0) {
//                     board[index][col] = value;
//                 } else if (board[index][col] == value) {
//                     board[index][col] *= 2;
//                     max_block_value = max(max_block_value, board[index][col]);
//                     index--;
//                 } else {
//                     board[--index][col] = value;
//                 }
//             }
//         }
//     } else if (direction == 2) { // Left
//         for (int row = 0; row < N; row++) {
//             int index = 0;
//             for (int col = 1; col < N; col++) {
//                 if (board[row][col] == 0) continue;
//                 int value = board[row][col];
//                 board[row][col] = 0;
//                 if (board[row][index] == 0) {
//                     board[row][index] = value;
//                 } else if (board[row][index] == value) {
//                     board[row][index] *= 2;
//                     max_block_value = max(max_block_value, board[row][index]);
//                     index++;
//                 } else {
//                     board[row][++index] = value;
//                 }
//             }
//         }
//     } else if (direction == 3) { // Right
//         for (int row = 0; row < N; row++) {
//             int index = N - 1;
//             for (int col = N - 2; col >= 0; col--) {
//                 if (board[row][col] == 0) continue;
//                 int value = board[row][col];
//                 board[row][col] = 0;
//                 if (board[row][index] == 0) {
//                     board[row][index] = value;
//                 } else if (board[row][index] == value) {
//                     board[row][index] *= 2;
//                     max_block_value = max(max_block_value, board[row][index]);
//                     index--;
//                 } else {
//                     board[row][--index] = value;
//                 }
//             }
//         }
//     }
//     return board;
// }

// void dfs(vector<vector<int>> board, int moves) {
//     if (moves == 5) return;

//     for (int i = 0; i < 4; i++) {
//         vector<vector<int>> new_board = move(board, i);
//         if (new_board != board) {
//             dfs(new_board, moves + 1);
//         }
//     }
// }

// void solve() {
//     cin >> N;
//     vector<vector<int>> board = readBoard();
//     dfs(board, 0);
//     cout << max_block_value << endl;
// }

// int main() {
//     solve();
//     return 0;
// }