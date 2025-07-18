# 사용자 입력을 받아 제곱을 계산하고 예외를 처리합니다.
try:
    # 사용자로부터 밑(base)과 지수(exponent)를 입력받음
    base_input = input("Enter number: ")
    exponent_input = input("Enter exponent: ")

    # 입력받은 문자열을 각각 float과 int로 변환
    base = float(base_input)
    exponent = int(exponent_input)

    # 0의 음수 거듭제곱 예외 처리 (0^(-n) = 1/0)
    if base == 0 and exponent < 0:
        raise ZeroDivisionError("Cannot calculate: division by zero (0 raised to negative power).")
    
    # 반복문을 사용하여 거듭제곱 계산
    result = 1
    
    if exponent >= 0:
        # 양수 지수인 경우: base를 exponent번 곱함
        for i in range(exponent):
            result *= base
    else:
        # 음수 지수인 경우: 1/(base^|exponent|)
        for i in range(-exponent):
            result *= base
        result = 1 / result

    # 결과 출력 (요구사항에 맞게 정수로 표현될 수 있도록 처리)
    if result == int(result):
        print(f"Result: {int(result)}")
    else:
        print(f"Result: {result}")

except ValueError:
    # 숫자로 변환할 수 없는 값이 입력된 경우 예외 처리
    print("Invalid number input.")
except ZeroDivisionError as e:
    # 0의 음수 거듭제곱인 경우 예외 처리
    print(str(e))