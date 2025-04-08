#!/bin/bash

set -e

# Determine version from VERSION file
VERSION=$(grep '^test=' VERSION | cut -d'=' -f2 | xargs)
PROD_VERSION=$(grep '^prod=' VERSION | cut -d'=' -f2 | xargs)

# Token fallback (use env if available, otherwise hardcoded)
TEST_TOKEN=${TEST_PYPI_TOKEN:-}
PROD_TOKEN=${PYPI_TOKEN:-pypi-xxxxxxxxxxxxxxxx--prodTokenHere}

# Choose environment
if [ "$1" == "--test" ]; then
  TEST_TOKEN=$(grep '^test-pypi=' PYPI_TOKEN | cut -d'=' -f2 | xargs)
  echo "🔧 Building and publishing to TestPyPI (version $VERSION)..."
  poetry version "$VERSION"
  echo "__version__ = \"$VERSION\"" > ./src/dbt_sqlx/__init__.py
  poetry build
  poetry publish -r dbt-sqlx-test -u __token__ -p "$TEST_TOKEN"
  
elif [ "$1" == "--prod" ]; then
  PROD_TOKEN=$(grep '^prod-pypi=' PYPI_TOKEN | cut -d'=' -f2 | xargs)
  echo "🚀 Building and publishing to PyPI (version $PROD_VERSION)..."
  poetry version "$PROD_VERSION"
  echo "__version__ = \"$PROD_VERSION\"" > ./src/dbt_sqlx/__init__.py
  poetry build
  poetry publish -u __token__ -p "$PROD_TOKEN"
  
else
  echo "❌ Usage: ./build.sh --test or ./build.sh --prod"
  exit 1
fi


# Function to bump patch version
bump_version() {
  local version=$1
  local major=$(echo "$version" | cut -d. -f1)
  local minor=$(echo "$version" | cut -d. -f2)
  local patch=$(echo "$version" | cut -d. -f3)
  local new_patch=$((patch + 1))
  echo "${major}.${minor}.${new_patch}"
}

# After successful publish, bump the version
if [ "$1" == "--test" ]; then
  NEW_VERSION=$(bump_version "$VERSION")
  sed -i "s/^test=$VERSION/test=$NEW_VERSION/" VERSION
  echo "✅ Bumped test version to $NEW_VERSION"
elif [ "$1" == "--prod" ]; then
  NEW_VERSION=$(bump_version "$PROD_VERSION")
  sed -i "s/^prod=$PROD_VERSION/prod=$NEW_VERSION/" VERSION
  echo "✅ Bumped prod version to $NEW_VERSION"
fi