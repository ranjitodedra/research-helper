# Research Helper Tools

## UIG (Unified Input Generator)

The UIG module combines `maintainRatio`, `NetworkGenerator`, `InputGenerator`, and `customer&bssLists` modules into a single unified interface. You only need to provide the total number of nodes, and it will automatically generate all necessary network configurations, matrices, and input files.

### Setup Instructions

#### 1. Create a Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
```

**Linux/Mac:**
```bash
python3 -m venv venv
```

#### 2. Activate the Virtual Environment

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

#### 3. Install Dependencies

Once the virtual environment is activated, install all required packages:

```bash
pip install -r requirements.txt
```

#### 4. Run the UIG Module

Navigate to the UIG directory and run the module:

```bash
cd UIG
python uig.py
```

The program will prompt you to enter the total number of nodes. For example:
```
Enter total number of nodes: 14
```

#### 5. Output Files

After running, the UIG module will generate several output files in the `UIG/` directory:

- **Network Configuration** (`*_network_config.txt`) - Contains the network structure, node labels, and types
- **Input Example** (`*_example.txt`) - Contains GA input, CPLEX matrices, and all calculated values
- **Visualization PNG** (`*.png`) - Visual representation of the network graph
- **JSON Input** (`*.json`) - JSON format for other modules
- **DAT Input** (`*.dat`) - DAT format for CPLEX optimization

### Troubleshooting

If you encounter an `ImportError` about NumPy and scikit-learn:
1. Make sure your virtual environment is activated
2. Verify that requirements are installed: `pip list`
3. Reinstall requirements: `pip install -r requirements.txt --upgrade`