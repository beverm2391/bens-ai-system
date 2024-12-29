# Code Conventions

## Structure
- Flat hierarchy where possible
- Feature-based folders only when necessary
- Tests next to implementation files

## Style
- Python: PEP 8
- Clear names over clever ones
- Comments only for complex logic
- Type hints on public interfaces

## Documentation
- README in each directory
- Docstrings: Google style
- Keep docs close to code
- Update docs with code changes

## Testing
- pytest
- Test files named: test_*.py
- Focus on critical paths
- Keep tests simple and readable

## Git
- Atomic commits
- Clear commit messages
- Feature branches when needed
- Main branch always stable 

## Package Management
- Install packages directly in environment with pip
- Do not maintain requirements.txt - we work in the environment directly
- Only document critical version dependencies if absolutely necessary

## Code Style
- Keep it simple
- Less code is better
- Challenge complexity 