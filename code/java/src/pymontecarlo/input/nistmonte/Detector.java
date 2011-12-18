package pymontecarlo.input.nistmonte;

import gov.nist.microanalysis.EPQLibrary.EPQException;
import gov.nist.microanalysis.NISTMonte.BremsstrahlungEventListener;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS;
import gov.nist.microanalysis.NISTMonte.XRayEventListener2;

import java.io.File;
import java.io.IOException;

/**
 * Interface for all detectors.
 * 
 * @author ppinard
 */
public interface Detector {

    /**
     * Setups the simulation and other listeners. This typically involves adding
     * action listeners to collect data for this detector. Note that the x-ray
     * and Bremsstrahlung event listener may be <code>null</code> if no x-ray
     * have to be detected.
     * 
     * @param mcss
     *            Monte Carlo simulation
     * @param xrel
     *            x-ray event listener
     * @param bel
     *            Bremsstrahlung event listener
     * @throws EPQException
     *             if an error occurs during the setup
     */
    public void setup(MonteCarloSS mcss, XRayEventListener2 xrel,
            BremsstrahlungEventListener bel) throws EPQException;



    /**
     * Saves the data collected by the detector inside a directory. If the data
     * is saved in one file, the base name can be the name of the file. If the
     * data is saved in multiple files, the base name can be the prefix of all
     * the files.
     * 
     * @param resultsDir
     *            directory where to save the results
     * @param baseName
     *            base name of the result file(s)
     * @throws IOException
     *             if an error occurs while saving the results
     */
    public void saveResults(File resultsDir, String baseName)
            throws IOException;



    /**
     * Saves a log of the detector parameters.
     * 
     * @param resultsDir
     *            directory where to save the log
     * @param baseName
     *            base name of the log file(s)
     * @throws IOException
     *             if an error occurs while saving the log
     */
    public void saveLog(File resultsDir, String baseName) throws IOException;

}
