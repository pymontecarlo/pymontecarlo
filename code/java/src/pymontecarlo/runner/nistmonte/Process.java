package pymontecarlo.runner.nistmonte;

import gov.nist.microanalysis.EPQLibrary.AlgorithmUser;
import gov.nist.microanalysis.EPQLibrary.EPQException;
import gov.nist.microanalysis.EPQLibrary.FromSI;
import gov.nist.microanalysis.EPQLibrary.Material;
import gov.nist.microanalysis.EPQLibrary.Strategy;
import gov.nist.microanalysis.NISTMonte.IMaterialScatterModel;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS.ElectronGun;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS.RegionBase;
import gov.nist.microanalysis.NISTMonte.PencilBeam;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Properties;
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

        saveLog(resultsDir, name, mcss);

        return showers;
    }



    /**
     * Saves the parameters of the simulation.
     * 
     * @param resultsDir
     *            results directory
     * @param baseName
     *            name of the simulation
     * @param mcss
     *            MonteCarloSS
     * @throws IOException
     *             if an error occurs while saving the log file
     */
    protected void saveLog(File resultsDir, String baseName, MonteCarloSS mcss)
            throws IOException {
        File logFile = new File(resultsDir, baseName + ".log");

        Properties props = new Properties();

        // Beam
        ElectronGun beam = mcss.getElectronGun();
        props.setProperty("beam.energy",
                Double.toString(FromSI.eV(beam.getBeamEnergy())));
        props.setProperty("beam.center.x", Double.toString(beam.getCenter()[0]));
        props.setProperty("beam.center.y", Double.toString(beam.getCenter()[1]));
        props.setProperty("beam.center.z", Double.toString(beam.getCenter()[2]));

        if (beam instanceof PencilBeam) {
            props.setProperty("beam.direction.x",
                    Double.toString(((PencilBeam) beam).getDirection()[0]));
            props.setProperty("beam.direction.y",
                    Double.toString(((PencilBeam) beam).getDirection()[1]));
            props.setProperty("beam.direction.z",
                    Double.toString(((PencilBeam) beam).getDirection()[2]));
        }

        // Geometry
        List<RegionBase> regions = mcss.getChamber().getSubRegions();
        RegionBase region;
        Material material;
        IMaterialScatterModel model;
        String key;
        for (int i = 0; i < regions.size(); i++) {
            key = "geometry.region." + i + ".";
            region = regions.get(i);
            material = region.getMaterial();
            model = region.getScatterModel();

            props.setProperty(key + "material.name", material.getName());
            props.setProperty(key + "material.density",
                    Double.toString(material.getDensity()));
            props.setProperty(key + "model.absorptionEnergy",
                    Double.toString(FromSI.eV(model.getMinEforTracking())));
        }

        // Model
        Strategy strategy = AlgorithmUser.getGlobalStrategy();
        for (String algClass : strategy.listAlgorithmClasses()) {
            props.setProperty("model." + algClass,
                    strategy.getAlgorithm(algClass).toString());
        }

        props.store(new FileOutputStream(logFile), "");
    }
}
