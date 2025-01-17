# Import packages and modules
import sys
# sys.path.append('scripts/')
import pandas as pd
import matplotlib as mpl
import seaborn as sns
import core_functions as cfs

modules = ['pandas', 'numpy']
for module in modules:
    try:
        print(module + ' ' + sys.modules[module].__version__)
    except:
        print(module + ' has no __version__ attribute')

sns.set_context('paper')
sns.set_style('ticks')
boxprops = {'edgecolor': 'k', 'linewidth': 0.5, 'facecolor': 'w'}
lineprops = {'color': 'k', 'linewidth': 0.5}
stripplot_kwargs = dict({'linewidth': 0.5, 'size': 3, 'alpha': 0.8})
boxplot_kwargs = dict({'boxprops': {'linewidth': 0, 'facecolor': 'w'}, 'medianprops': {'linewidth': 1},
                       'whiskerprops': {'linewidth': 0}, 'capprops': {'linewidth': 0},
                       'width': 0.8, 'whis': (10, 90)})

###### USER INPUTS ######

# Allele frequency inputs

# Read meta-information file
input_filepath = input("Please enter input filepath here: ")
input_file = pd.read_csv(input_filepath)
print(input_file.head(2))

# check for NaN values i.e. blank rows
if input_file.isnull().values.any():
    input_file = cfs.clean_input_file(input_file)

# check if inputs in meta-information file are correctly formatted
cfs.check_input_file(input_file)

# User inputs read_count_filter
global read_count_percent_cutoff
read_count_percent_cutoff_input = input("Please enter percent to use for filtering low read counts here. "
                                        "Common cutoffs are 1-2%. ")
read_count_percent_cutoff = float(read_count_percent_cutoff_input)

# User inputs path to correlation input file, or leaves blank if none
corr_corr_inputpath = input("Please enter correlation input filepath here: ")
if corr_corr_inputpath == '':
    corr_input = None
    print('No correlation input file.')
else:
    corr_input = pd.read_csv(corr_corr_inputpath)
    corr_input.head()

# User inputs string used to name files ('BEV' or 'NGBEV')
global bev_string_id
bev_string_id = input(
    'Please enter either \'BEV\' or \'NGBEV\' to indicate which string is used when naming your CRISPResso files.')
if ((bev_string_id != 'BEV') and (bev_string_id != 'NGBEV')):
    raise Exception(
        'Invalid input. Please enter either \'BEV\' or \'NGBEV\' to specify which string is used in CRISPResso file names. Be careful not to add any extra spaces.')

# User inputs path to CRISPResso files
global CRISPResso_filepath
CRISPResso_filepath = input("Please enter CRISPResso filepath here: ")
CRISPResso_filepath = cfs.check_folder_filepath(CRISPResso_filepath)
print(CRISPResso_filepath)

# User inputs filepath to store allele_freq output tables
global output_filepath
# output_filepath = '../../RemovingPrimerInput_NotebookUpdate/allele_freq'
output_filepath = input("Please enter output folder filepath here: ")
output_filepath = cfs.check_folder_filepath(output_filepath)
print(output_filepath)

# User inputs column labels and heatmap filename
global time1
time1 = input("Please input the label for the first %Reads column (e.g. D7, low)")
global time2
time2 = input("Please input the label for the second %Reads column (e.g. D21, high)")
global heatmap_filename
heatmap_filename = input("Please enter the filename for the heatmap.")

# Nucleotide percentage inputs

# User inputs type of base editor to determine x-axis labels (e.g. ABE -> Position of A)
global be_type
be_type_input = input(
    "Please specify the type of base editor used in the input samples by entering 'A' for A base editor or 'C' for C base editor: ")

# Make sure a base editor is selected and not default value
if (be_type_input != 'A') and (be_type_input != 'C'):
    raise Exception('Invalid input. Please enter either A or C to specify base editor.')

else:
    # Add 'BE' to be_type
    be_type = be_type_input + 'BE'

# Editing efficiency input

# User inputs name of gene being targeted
global experiment
experiment = input("Please enter gene name here: ")

#### FUNCTIONS ####

###### ALLELE FREQUENCIES SECTION ######

# Run function
cfs.run(input_file, corr_input, bev_string_id, CRISPResso_filepath, read_count_percent_cutoff, output_filepath)

# Run heatmap function
cfs.heatmaps(df=input_file,
             vmin=-2,
             vmax=2,
             filepath=output_filepath,
             time1=time1,
             time2=time2,
             filename=heatmap_filename
             )

print('Allele frequencies analysis complete.')

###### NUCLEOTIDE PERCENTAGE SECTION ######

# make input df with columns BEV, offset, rev_com, left_lim, right_lim, primer, width, height
input_df = pd.DataFrame()

# check for NaN values i.e. blank rows
if input_file.isnull().values.any():
    input_file = cfs.clean_input_file(input_file)

allele_freq_input_df = input_file

BEV_test_df = allele_freq_input_df[['sgRNA_sequence', 'BEV_test', 'primer']].copy()
BEV_test_df['type'] = 'test'
BEV_test_df = BEV_test_df.copy().rename(columns={'sgRNA_sequence': 'guide_seq', 'BEV_test': 'BEV'})

BEV_ref_df = allele_freq_input_df[['sgRNA_sequence', 'BEV_ref', 'primer']].copy()
BEV_ref_df['type'] = 'ref'
BEV_ref_df = BEV_ref_df.copy().rename(columns={'sgRNA_sequence': 'guide_seq', 'BEV_ref': 'BEV'})

input_df = pd.concat([BEV_ref_df, BEV_test_df]).reset_index(drop=True)

# Set x-axis limits
input_df['left_lim'] = -25
input_df['right_lim'] = 25

# Set plot dimensions
input_df['width'] = 6
input_df['height'] = 6

print(input_df.head(2))

# Run functions row by row
for i, row in input_df.iterrows():
    print(row['BEV'])
    bev_list = row['BEV'].split(';')
    output_name = '_'.join(bev_list)  # +'_'+row['primer']
    # bev_df = get_bev_df(bev_list,row['rev_com'],output_name,row['primer'], row['guide_seq'])
    bev_df = cfs.get_bev_df(bev_list, output_name, row['guide_seq'], be_type, CRISPResso_filepath,
                            bev_string_id, output_filepath)
    cfs.make_nuc_per_plot(bev_df, row['left_lim'], row['right_lim'], bev_list, row['width'], row['height'],
                          be_type, output_name, output_filepath)

    # break

print('Nucleotide percentage analysis complete.')

###### EDITING EFFICIENCY SECTION ######

# Filepath where outputs from nucleotide percentage section are stored
global nuc_per_filepath
# nuc_per_filepath = '../../AudreyData/TP53/ABE_v8/nucleotide_percentage'
# nuc_per_filepath = input("Please enter filepath to folder with nucleotide percentage outputs here: ")
nuc_per_filepath = output_filepath + 'nucleotide_percentage'
nuc_per_filepath = cfs.check_folder_filepath(nuc_per_filepath)
print(nuc_per_filepath)

# Generate editing efficiency table
df = cfs.run_editing_eff(input_file, nuc_per_filepath, output_filepath, experiment, be_type)
save_filepath = output_filepath + 'editing_efficiency_input.csv'
df.to_csv(save_filepath)

# Filter by editing window for plotting purposes
df = df.copy().drop('sg', axis=1).drop_duplicates()
if be_type == 'ABE':
    df.loc[(df['Position'] >= 4) & (df['Position'] <= 8) & (df['Nucleotide'] == 'G'), 'Position'].value_counts()
    nuc = 'G'
elif be_type == 'CBE':
    df.loc[(df['Position'] >= 4) & (df['Position'] <= 8) & (df['Nucleotide'] == 'T'), 'Position'].value_counts()
    nuc = 'T'

fig, ax = cfs.make_editing_eff_plot(df, nuc, [experiment], be_type, output_filepath)

print('Editing efficiency analysis complete.')
print('Analysis complete.')

