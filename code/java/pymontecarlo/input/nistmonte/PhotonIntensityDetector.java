package pymontecarlo.input.nistmonte;

import gov.nist.microanalysis.EPQLibrary.EPQException;
import gov.nist.microanalysis.EPQLibrary.Element;
import gov.nist.microanalysis.EPQLibrary.ToSI;
import gov.nist.microanalysis.EPQLibrary.XRayTransition;
import gov.nist.microanalysis.EPQLibrary.XRayTransitionSet;
import gov.nist.microanalysis.NISTMonte.BremsstrahlungEventListener;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS;
import gov.nist.microanalysis.NISTMonte.XRayAccumulator;
import gov.nist.microanalysis.NISTMonte.XRayEventListener2;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Properties;
import java.util.Set;

import ptpshared.io.CSVWriter;

/**
 * Detector to record intensity of photons.
 * 
 * @author ppinard
 */
public class PhotonIntensityDetector extends PhotonDetector {

    /** Stores the <code>XRayAccumulator</code> for each element. */
    private XRayAccumulator xrayAccumulator = null;



    @Override
    protected void saveAsProperties(Properties props) {
        super.saveAsProperties(props);

        Set<Element> elements = new HashSet<Element>();
        for (XRayTransition xrayTransition : xrayAccumulator.getTransitions()) {
            elements.add(xrayTransition.getElement());
        }
        props.setProperty("accumulators", elements.toString());
    }



    /**
     * Creates a new <code>PhotonIntensityDetector</code>.
     * 
     * @param takeOffAngle
     *            elevation from the x-y plane (in radians)
     * @param azimuthAngle
     *            counter-clockwise angle from the positive x-axis in the x-y
     *            plane (in radians)
     */
    public PhotonIntensityDetector(double takeOffAngle, double azimuthAngle) {
        super(takeOffAngle, azimuthAngle);
    }



    /**
     * Creates a new <code>PhotonIntensityDetector</code>.
     * 
     * @param position
     *            detector position in the chamber (in meters)
     */
    public PhotonIntensityDetector(double[] position) {
        super(position);
    }



    @Override
    public void setup(MonteCarloSS mcss, XRayEventListener2 xrel,
            BremsstrahlungEventListener bel) throws EPQException {
        double e0 = ToSI.eV(50);
        double emax = mcss.getBeamEnergy();

        XRayTransitionSet xrayTransitions = new XRayTransitionSet();

        XRayTransitionSet elementXrayTransitions;
        for (Element element : mcss.getElementSet()) {
            elementXrayTransitions = new XRayTransitionSet(element, e0, emax);

            xrayTransitions =
                    XRayTransitionSet.union(xrayTransitions,
                            elementXrayTransitions);
        }

        xrayAccumulator = new XRayAccumulator(xrayTransitions.getTransitions());
        xrel.addActionListener(xrayAccumulator);
    }



    @Override
    public void saveResults(File resultsDir, String baseName)
            throws IOException {
        File resultsFile = new File(resultsDir, baseName + ".csv");
        CSVWriter writer = new CSVWriter(new FileWriter(resultsFile));

        writer.writeNext("Element", "Atomic number", "Transition",
                "Energy (eV)", "Emitted", "Generated");

        List<XRayTransition> xrayTransitions = new ArrayList<XRayTransition>();
        xrayTransitions.addAll(xrayAccumulator.getTransitions());
        Collections.sort(xrayTransitions);

        Element element;
        String elementName;
        int atomicNumber;
        String xrayTransitionName;
        double emittedIntensity;
        double generatedIntensity;
        double xrayTransitionEnergy;
        for (XRayTransition xrayTransition : xrayTransitions) {
            element = xrayTransition.getElement();
            elementName = element.toString();
            atomicNumber = element.getAtomicNumber();

            xrayTransitionName = xrayTransition.getIUPACName();

            try {
                xrayTransitionEnergy = xrayTransition.getEnergy_eV();
            } catch (EPQException e) {
                xrayTransitionEnergy = Double.NaN;
            }

            emittedIntensity = xrayAccumulator.getEmitted(xrayTransition);
            generatedIntensity = xrayAccumulator.getGenerated(xrayTransition);

            writer.writeNext(elementName, atomicNumber, xrayTransitionName,
                    xrayTransitionEnergy, emittedIntensity, generatedIntensity);
        }

        writer.close();
    }

}
