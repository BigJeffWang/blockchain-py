# 这种写法 暂时搁置 change 统一都为0
# def get_subacct_key(self, count, begin=0):
#     end = begin + count
#     slice = Wallet.slice
#     change = 1
#     index = slice
#     index_end = 0
#     change_begin = 0
#     index_begin = 0
#     flag = 0
#     counter = begin
#     if end <= slice:
#         index = end
#     else:
#         change = end // slice
#         index_end = end % slice
#         if index_end != 0:
#             change += 1
#     if begin > 0:
#         if begin < slice:
#             index_begin = begin
#         else:
#             change_begin = begin // slice
#             index_begin = begin % slice
#
#     subacct_info_dict = {}
#     for i in range(change_begin, change):
#         if i == change - 1:
#             if index_end > 0:
#                 index = index_end
#         for j in range(index_begin, index):
#             subacct_info_dict[str(counter)] = self.generate_subacct_info(i, j)
#             counter += 1
#         if flag == 0:
#             index_begin = 0
#             flag += 1
#     return subacct_info_dict