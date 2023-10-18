python3 helper/build.py
build_files=$(git ls-files | grep '^build/')

# Check if there are any staged changes in the 'build' directory
if [ -n "$build_files" ]; then
  # Stage all changes in the 'build' directory
  git add $build_files
fi
