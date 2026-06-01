# Contributing to Multi-Epitope Vaccine Design Pipeline

Thank you for your interest in contributing to this project! This pipeline represents a significant advancement in computational vaccinology, and community contributions are welcome to extend its capabilities and applications.

## 🤝 Ways to Contribute

### 1. Bug Reports and Issues
- Report bugs through GitHub Issues
- Include detailed description and steps to reproduce
- Provide system information and Python version
- Include relevant log files or error messages

### 2. Feature Requests
- Suggest new analysis methods or validation approaches
- Propose support for additional pathogens
- Request integration with new bioinformatics tools
- Share ideas for performance improvements

### 3. Code Contributions
- Bug fixes and performance improvements
- New analysis modules or validation methods
- Documentation improvements
- Unit tests and quality assurance

### 4. Scientific Contributions
- Experimental validation of predicted epitopes
- New statistical methods for epitope selection
- Alternative construct design strategies
- Population coverage analysis improvements

## 🛠️ Development Setup

### Prerequisites
```bash
python >= 3.8
git
```

### Setup Development Environment
```bash
# Clone your fork
git clone https://github.com/[your-username]/multi-epitope-vaccine-design.git
cd multi-epitope-vaccine-design

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Install development dependencies
pip install pytest black flake8 mypy
```

### Run Tests
```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src

# Run linting
flake8 src/
black --check src/
```

## 📋 Development Guidelines

### Code Style
- Follow PEP 8 style guidelines
- Use Black for code formatting: `black src/`
- Maximum line length: 88 characters
- Use type hints where appropriate
- Add docstrings for all functions and classes

### Testing
- Write unit tests for new functions
- Maintain test coverage above 80%
- Include integration tests for major features
- Test with multiple Python versions (3.8, 3.9, 3.10+)

### Documentation
- Update docstrings for any modified functions
- Add examples for new features
- Update README.md if interface changes
- Include scientific rationale for new methods

### Git Workflow
1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/new-analysis-method`
3. **Make your changes** with clear, atomic commits
4. **Write/update tests** for your changes
5. **Update documentation** as needed
6. **Run the test suite** to ensure nothing is broken
7. **Submit a pull request** with clear description

### Commit Messages
Use clear, descriptive commit messages:
```
feat: add support for influenza H1N1 epitope prediction
fix: resolve IEDB parsing error for MHC-II alleles
docs: update methodology with new statistical methods
test: add unit tests for construct validation
```

## 🧪 Scientific Contributions

### Experimental Validation
If you validate predicted epitopes experimentally:
- Share protocols and results
- Include statistical analysis of binding assays
- Document any deviations from predicted values
- Consider co-authorship on publications

### New Methods
When proposing new analysis methods:
- Provide scientific justification
- Include benchmarking against existing methods
- Add relevant literature references
- Ensure reproducibility

### Data Contributions
- New pathogen sequences and annotations
- HLA allele frequency data for understudied populations
- Experimental binding data for benchmarking
- Structural data for docking validation

## 🎯 Priority Areas for Contribution

### High Priority
1. **Experimental validation** of predicted epitopes
2. **Performance optimization** for large-scale analysis
3. **Additional pathogen support** (influenza, HIV, etc.)
4. **Population coverage improvements** for global diversity

### Medium Priority
1. **Alternative validation methods** (AllerHunter, etc.)
2. **Enhanced visualization** capabilities
3. **Batch processing optimization**
4. **Documentation improvements**

### Future Directions
1. **Machine learning integration** for epitope prediction
2. **Structural homology analysis**
3. **Evolutionary pressure analysis**
4. **Clinical trial data integration**

## 📚 Resources

### Scientific Background
- [IEDB Analysis Resource](http://tools.iedb.org/)
- [NetMHCpan Documentation](https://services.healthtech.dtu.dk/service.php?NetMHCpan-4.1)
- [Vaccine Design Reviews](https://www.nature.com/subjects/vaccines)

### Technical Documentation
- [BioPython Tutorial](https://biopython.org/wiki/Documentation)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Python Testing Best Practices](https://realpython.com/pytest-python-testing/)

## 🔍 Code Review Process

### Pull Request Requirements
- [ ] Clear description of changes
- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No merge conflicts

### Review Criteria
1. **Scientific Accuracy**: Methods are scientifically sound
2. **Code Quality**: Readable, maintainable, well-documented
3. **Testing**: Adequate test coverage
4. **Performance**: No significant performance regressions
5. **Documentation**: Clear and comprehensive

## 🏷️ Issue Labels

- `bug`: Something isn't working
- `enhancement`: New feature or request  
- `documentation`: Improvements or additions to documentation
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention is needed
- `question`: Further information is requested
- `scientific`: Requires domain expertise
- `performance`: Performance-related improvements

## 🤔 Questions?

- **General Questions**: Use GitHub Discussions
- **Bug Reports**: Create GitHub Issues
- **Scientific Collaboration**: Contact maintainers directly
- **Feature Requests**: Open GitHub Issues with detailed descriptions

## 📧 Contact

**Project Maintainer**: Fabian Alvarez-Primo, PhD  
**Email**: fpalvarez23@gmail.com  
**GitHub**: [@fabzy4L](https://github.com/fabzy4L)

## 🙏 Recognition

Contributors will be acknowledged in:
- Repository contributors list
- Publication acknowledgments (for significant contributions)
- Release notes
- Documentation credits

Thank you for helping advance computational vaccinology! 🧬

---

**Note**: This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). By participating, you are expected to uphold this code.