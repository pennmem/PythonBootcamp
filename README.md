# Python Bootcamp

These are notes for the Computational Memory Lab's Python Bootcamp.  They are also a good introduction to performing EEG analyses, and you can use them as a resource for learning these tools and methods.

# Making use of this tutorial

This tutorial can be made use of on your own system after obtaining the
CMLExamples data set (contact kahana-sysadmin@sas.upenn.edu to receive
access to these files) or directly on the Rhino computing cluster if you
have access to this.

# Getting started on Rhino

If you have been provided with an account on the Rhino computing cluster, these instructions will help you access and setup your account to the point where you can follow these bootcamp notes and perform analyses.  If you are using another system, skip ahead to Setting up JupyterLab.

### Setting up your Rhino2 Account

1\. You can log in to Rhino2 in a terminal window by using any ssh client
to ssh into rhino as follows, replacing the "username" with your username:

    ssh username@rhino2.psych.upenn.edu

and then typing your temporary password when prompted. Once successfully
connected, type:

    passwd

to change your password to something only you know. Please do this as soon as
you have the time!

(As a general tip to Windows users without access to Terminal, we recommend
using Cygwin <https://www.cygwin.com/> or the Ubuntu subsystem
<https://docs.microsoft.com/en-us/windows/wsl/install-win10>)

2\. Once you have your password set up, check to be sure you can log in to
JupyterLab, where you'll be doing most of the bootcamp work. If you are
connected to the internet on UPenn's campus, you only need to go to
[https://rhino2.psych.upenn.edu:8200](https://rhino2.psych.upenn.edu:8200/) to
access JupyterLab. If you are connecting remotely, follow the rest of this
step. In a terminal where ssh is accessible, replace the "username" with your
username, and open an ssh tunnel by typing:

    ssh -L8000:rhino2.psych.upenn.edu:8200 username@rhino2.psych.upenn.edu

followed by entering your rhino password. In your web browser, navigate to:

[https://127.0.0.1:8000](https://127.0.0.1:8000)

and you should see the JupyterLab interface pop up!  Note that the "s" on https is critical for this to work.  Your browser might warn about this being an insecure connection or invalid certificate, given that 127.0.0.1 (direct to the ssh tunnel on your own computer) is not rhino.  Override this warning and connect anyway, because we are using ssh to provide better security here.  If the connection still fails, go back and make sure that your ssh tunnel was correctly created.

### Installing CMLReader

In your ssh terminal to rhino, enter the following commands:

    conda create -y -n environmentname python=3.7
    source activate environmentname
    conda install -c pennmem cmlreaders

### Rhino Specific Guide

Rhino specific instructions for internal usage beyond the example data set,
such as usage examples for CMLReader, are in the Rhino\_Usage.ipynb notebook.

# Setting up JupyterLab

Next, you'll need to install a suite of tools for EEG analysis. First,
install MNE by typing the following (be sure you're in the Anaconda
"environment" you just created in Step 1, by typing "source activate
environmentname"). Note that this may take a while, because MNE has a
lot of dependencies:

    conda install -c conda-forge mne

Next, install PTSA, which is another set of EEG tools developed by
former lab members:

    conda install -c pennmem ptsa

Finally, you'll need to link JupyterLab with your specific Python
installation.  While still logged in and in your Anaconda "environment",
type:

    conda install ipykernel

and once that's done:

    python -m ipykernel install --user --name environmentname --display-name "environmentname"

You should be all set! Next time you log in to your JupyterLab account,
you should see an option to launch a new notebook with "environmentname"
as your Python environment. If you've been logged in to JupyterLab this
whole time, you may need to log out and log back in again to see this
change take effect.

### Getting the PythonBootcamp JupyterLab notes

Ssh into rhino with a terminal, and type:

    git clone 'https://github.com/pennmem/PythonBootcamp'

### Setting up the CMLExamples files

You will need to provide each notebook code example making use of the
CMLExamples files with how to find the files.  The simplest way if your
system supports it is to make a symbolic link in your PythonBootcamp
directory to these files.  For example, on Rhino this is currently
(temporarily) done by going into the PythonBootcamp directory and entering:

    ln -s /data/examples

### Learning how to use the tools and perform analyses

In JupyterLab, navigate to the lecture notes you downloaded using
the file browser section on the left, open the lecture notes, and
proceed through them in order. If appropriate for your background and
situation, jump ahead to the relevant sections to see syntax examples
for common analyses and for using the common tools used by the
Computational Memory Lab.

