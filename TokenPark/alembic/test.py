


def thirdMax(self, nums):
    """
    :type nums: List[int]
    :rtype: int
    """
    size = len(nums)
    if size <= 2:
        for i in range(len(nums) - 1):
            for j in range(len(nums) - i - 1):
                if nums[j] < nums[j + 1]:
                    nums[j], nums[j + 1] = nums[j + 1], nums[j]
        return nums[0]
    else:
        for i in range(len(nums) - 1):
            for j in range(len(nums) - i - 1):
                if nums[j] < nums[j + 1]:
                    nums[j], nums[j + 1] = nums[j + 1], nums[j]
        flag = True
        index = 2
        while flag:
            if nums.count(nums[index]) > 1:
                index = index - 1
                if index == -1:
                    return nums[0]
            else:
                return nums[index]

nums = [1, 2, 3, 4, 3]
print(thirdMax(nums))