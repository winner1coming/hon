#定义服务器提供的服务方法
#1、两个数的加法
def Add(a, b ) :
    return a + b

#2、两个数的乘法
def Mul(a , b ) :
    return a * b

#3、两个数的减法
def Minus(a , b) :
    return a - b

#4、一个数的平方数
def Square(a ) :
    return a * a

#5、一个数的立方数
def Cube(a ) :
    return a * a * a

#6、取余
def Takeover(a, b):
    if b != 0:
        return a % b
    else:
        print("Tbakeover Error!!The divisor is 0!")
        return "Error 1"

#7、除法
def Division(a , b):
    if b != 0:
        return a / b
    else:
        print("Division Error!!The divisor is 0!")
        return "Error 2"

#8、求数组的和
def Sum(nums) :
    if len(nums) != 0:
        sum = 0
        for i in nums:
            sum += i
        return sum
    else:
        print("Nums is empty! No Sum!")
        return "Error 3"

#9、求数组的最大值
def Max(nums):
    if len(nums) != 0:
        return max(nums)
    else:
        print("Nums is empty! No Max!")
        return "Error 4"
    
#10、按序降序排序数组
def Sort(nums ):
    if len(nums) != 0:
        return sorted(nums, reverse=True)
    else:
        print("Nums is empty! Not Sort!")
        return "Error 5"