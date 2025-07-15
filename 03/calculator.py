def calculate_sum(n):
    """1부터 n까지의 합(등차수열의 합)을 계산합니다."""
    return n * (n + 1) // 2

def main():
    """
    사용자로부터 한 줄의 수식을 입력받아 계산 결과를 출력합니다.
    - 사칙연산: "10 + 5"
    - 보너스 기능: "100" (1부터 100까지의 합)
    """
    expression = input("Enter expression: ")
    parts = expression.split()

    try:
        # 보너스 기능: 입력된 부분이 하나이고 숫자인 경우
        if len(parts) == 1:
            num = int(parts[0])
            result = calculate_sum(num)
            print(f"Result: {result}")
            return

        # 사칙연산: 입력된 부분이 세 개인 경우
        if len(parts) == 3:
            num1 = float(parts[0])
            operator = parts[1]
            num2 = float(parts[2])

            if operator == '+':
                result = num1 + num2
            elif operator == '-':
                result = num1 - num2
            elif operator == '*':
                result = num1 * num2
            elif operator == '/':
                if num2 == 0:
                    print("Error: Division by zero.")
                    return
                result = num1 / num2
            else:
                print("Invalid operator.")
                return
            
            print(f"Result: {result}")
        
        else:
            # 입력 형식이 잘못된 경우
            print("Invalid expression format.")

    except ValueError:
        # 숫자로 변환할 수 없는 값이 입력된 경우
        print("Invalid number format in expression.")
    except Exception as e:
        # 기타 예외 처리
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    main()
