lines = open('update_mock_course_data.py', 'r', encoding='utf-8').readlines()
line47 = lines[46]
print('Line 47:', repr(line47))
print('Quote count:', line47.count('"'))
print('Triple quote test:', '"""' in line47)
