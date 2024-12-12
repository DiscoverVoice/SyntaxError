
    #include <iostream>
    #include <vector>
    #include <memory>
    using namespace std;

    int main() {
        int* ptr = new int[10];
        cout << ptr[5] << endl; // 초기화되지 않은 메모리 읽기

        delete[] ptr;
        cout << ptr[0] << endl; // 해제된 메모리 접근 (Use-after-free)
        int k = 5/0;
        return 0;
    }
    