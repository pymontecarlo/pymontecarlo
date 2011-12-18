package pymontecarlo.runner.nistmonte;

import gov.nist.microanalysis.EPQLibrary.EPQException;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS;

import java.io.File;
import java.io.IOException;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Set;

import org.jdom.Element;

import ptpshared.jdom.JDomUtils;
import pymontecarlo.input.nistmonte.Detector;
import pymontecarlo.input.nistmonte.Limit;
import pymontecarlo.input.nistmonte.ShowersLimit;
import pymontecarlo.io.nistmonte.OptionsExtractor;

/**
 * Runner for NistMonte.
 * 
 * @author ppinard
 */
public class Process {

    /** XML file of the options. */
    private final File optionsFile;

    /** Results directory. */
    private final File resultsDir;



    /**
     * Creates a new runner process.
     * 
     * @param optionsFile
     *            XML file of the options
     * @param resultsDir
     *            results directory
     */
    public Process(File optionsFile, File resultsDir) {
        if (optionsFile == null)
            throw new NullPointerException("options file == null");
        this.optionsFile = optionsFile;

        if (resultsDir == null)
            throw new NullPointerException("results dir == null");
        if (!resultsDir.isDirectory())
            throw new IllegalArgumentException("resultsDir must be a directory");
        this.resultsDir = resultsDir;
    }



    /**
     * Returns the results directory.
     * 
     * @return results directory
     */
    public File getResultsDir() {
        return resultsDir;
    }



    /**
     * Returns the options extractor to use to read the options XML file.
     * 
     * @return options extractor
     */
    protected OptionsExtractor getOptionsExtractor() {
        return OptionsExtractor.getDefault();
    }



    /**
     * Runs a simulation.
     * 
     * @return number of electron simulated
     * @throws EPQException
     *             if an error occurs while setting up the simulation or running
     *             it
     * @throws IOException
     *             if an error occurs while reading the options
     */
    public int run() throws EPQException, IOException {
        // Extract from options XML file
        Element root = JDomUtils.loadXML(optionsFile).getRootElement();

        OptionsExtractor extractor = getOptionsExtractor();
        extractor.extract(root);

        String name = extractor.getName();
        MonteCarloSS mcss = extractor.getMonteCarloSS();
        Map<String, Detector> detectors = extractor.getDetectors();
        Set<Limit> limits = extractor.getLimits();

        // Get the number of showers
        int showers = 0;
        for (Limit limit : limits) {
            if (limit instanceof ShowersLimit) {
                showers = ((ShowersLimit) limit).getMaximumShowers();
            }
        }

        if (showers == 0)
            throw new EPQException("No ShowersLimit specified.");

        // Run
        mcss.runMultipleTrajectories(showers);

        // Save results and log
        String baseName;
        Detector detector;
        for (Entry<String, Detector> entry : detectors.entrySet()) {
            baseName = name + "_" + entry.getKey();
            detector = entry.getValue();

            detector.saveResults(resultsDir, baseName);
            detector.saveLog(resultsDir, baseName);
        }

        return showers;
    }
}
