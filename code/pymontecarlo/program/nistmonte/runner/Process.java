package pymontecarlo.program.nistmonte.runner;

import gov.nist.microanalysis.EPQLibrary.AlgorithmUser;
import gov.nist.microanalysis.EPQLibrary.EPQException;
import gov.nist.microanalysis.EPQLibrary.FromSI;
import gov.nist.microanalysis.EPQLibrary.Material;
import gov.nist.microanalysis.EPQLibrary.Strategy;
import gov.nist.microanalysis.NISTMonte.BremsstrahlungEventListener;
import gov.nist.microanalysis.NISTMonte.IMaterialScatterModel;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS.ElectronGun;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS.RegionBase;
import gov.nist.microanalysis.NISTMonte.PencilBeam;
import gov.nist.microanalysis.NISTMonte.XRayEventListener2;

import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Properties;
import java.util.Set;
import java.util.zip.ZipOutputStream;

import org.jdom.Element;

import ptpshared.jdom.JDomUtils;
import pymontecarlo.program.nistmonte.input.Detector;
import pymontecarlo.program.nistmonte.input.Limit;
import pymontecarlo.program.nistmonte.input.PhotonDetector;
import pymontecarlo.program.nistmonte.input.ShowersLimit;
import pymontecarlo.program.nistmonte.io.OptionsExtractor;
import pymontecarlo.util.ZipUtil;

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
        report(0.0, "Loading options file");
        Element root = JDomUtils.loadXML(optionsFile).getRootElement();

        OptionsExtractor extractor = getOptionsExtractor();
        extractor.extract(root);

        String name = extractor.getName();
        MonteCarloSS mcss = extractor.getMonteCarloSS();
        Map<String, Detector> detectors = extractor.getDetectors();
        Set<Limit> limits = extractor.getLimits();

        // Create listeners
        XRayEventListener2 xrel = getXRayEventListener(mcss, detectors);
        if (xrel != null)
            mcss.addActionListener(xrel);

        BremsstrahlungEventListener bel =
                getBremsstrahlungEventListener(mcss, detectors);
        if (bel != null)
            mcss.addActionListener(bel);

        // Register detectors
        for (Detector detector : detectors.values())
            detector.setup(mcss, xrel, bel);

        // Register limits and get the number of showers
        int showers = 0;
        for (Limit limit : limits) {
            if (limit instanceof ShowersLimit) {
                showers = ((ShowersLimit) limit).getMaximumShowers();
            } else {
                limit.setup(mcss, xrel, bel);
            }
        }

        if (showers == 0)
            throw new EPQException("No ShowersLimit specified.");

        // Run
        report(0.0, "Running showers");

        int fraction = 25;
        for (int n = 0; n < fraction; n++) {
            report((double) n / fraction, "Running showers");
            mcss.runMultipleTrajectories(showers / fraction);
        }

        // Create ZIP
        report(1.0, "Saving results");
        File resultsZip = new File(resultsDir, name + ".zip");
        OutputStream out =
                new BufferedOutputStream(new FileOutputStream(resultsZip));
        ZipOutputStream zipOutput = new ZipOutputStream(out);

        // Save results and log
        String key;
        Detector detector;
        for (Entry<String, Detector> entry : detectors.entrySet()) {
            key = entry.getKey();
            detector = entry.getValue();

            detector.saveResults(zipOutput, key);
            detector.saveLog(zipOutput, key);
        }

        // Create keys.ini
        StringBuffer buf = new StringBuffer();
        buf.append("[keys]\n");

        for (Entry<String, Detector> entry : detectors.entrySet())
            buf.append(entry.getKey() + " = " + entry.getValue().getTag()
                    + "\n");

        ZipUtil.saveStringBuffer(zipOutput, "keys.ini", buf);

        zipOutput.close();
        out.close();

        // Save overall log
        saveLog(resultsDir, name, mcss);

        return showers;
    }



    /**
     * Checks the detector and returns the x-ray event listener. The listener
     * will be <code>null</code> if there is no photon detector.
     * 
     * @param mcss
     *            MonteCarloSS
     * @param detectors
     *            detectors
     * @return x-ray event listener or <code>null</code>
     * @throws EPQException
     *             if an error occurs while creating the listener
     */
    private XRayEventListener2 getXRayEventListener(MonteCarloSS mcss,
            Map<String, Detector> detectors) throws EPQException {
        double[] detectorPosition = null;
        for (Detector detector : detectors.values()) {
            if (detector instanceof PhotonDetector) {
                detectorPosition =
                        ((PhotonDetector) detector).getDetectorPosition();
            }
        }

        if (detectorPosition != null) {
            return new XRayEventListener2(mcss, detectorPosition);
        } else {
            return null;
        }
    }



    /**
     * Checks the detector and returns the Bremsstrahlung event listener. The
     * listener will be <code>null</code> if there is no photon detector.
     * 
     * @param mcss
     *            MonteCarloSS
     * @param detectors
     *            detectors
     * @return Bremsstrahlung event listener or <code>null</code>
     * @throws EPQException
     *             if an error occurs while creating the listener
     */
    private BremsstrahlungEventListener getBremsstrahlungEventListener(
            MonteCarloSS mcss, Map<String, Detector> detectors)
            throws EPQException {
        double[] detectorPosition = null;
        boolean requiresBremsstrahlung = false;
        for (Detector detector : detectors.values()) {
            if (detector instanceof PhotonDetector) {
                detectorPosition =
                        ((PhotonDetector) detector).getDetectorPosition();
                requiresBremsstrahlung =
                        requiresBremsstrahlung
                                || ((PhotonDetector) detector)
                                        .requiresBremsstrahlung();
            }
        }

        if (detectorPosition != null && requiresBremsstrahlung) {
            return new BremsstrahlungEventListener(mcss, detectorPosition);
        } else {
            return null;
        }
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



    /**
     * Report progress and status.
     * 
     * @param progress
     *            current progress (between 0.0 and 1.0)
     * @param status
     *            current status
     */
    protected void report(double progress, String status) {
        System.out.println(progress + "\t" + status);
        System.out.flush();
    }
}
