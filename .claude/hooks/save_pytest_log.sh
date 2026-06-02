#!/bin/bash
input=$(cat)

command=$(echo "$input" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(d.get('tool_input', {}).get('command', ''))
" 2>/dev/null)

if echo "$command" | grep -q "pytest"; then
    output=$(echo "$input" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(d.get('tool_response', {}).get('output', ''))
" 2>/dev/null)

    timestamp=$(date +"%Y-%m-%d_%H-%M-%S")
    log_file="/Users/user/PycharmProjects/PythonFridaysSchool/logs/pytest_${timestamp}.log"
    {
        echo "Command: $command"
        echo "Date: $(date)"
        echo "---"
        echo "$output"
    } > "$log_file"
fi